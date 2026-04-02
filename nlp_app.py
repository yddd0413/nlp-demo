import streamlit as st
import nltk
from nltk.wsd import lesk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.tree import Tree
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import re
import warnings
warnings.filterwarnings('ignore')

nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('maxent_ne_chunker_tab', quiet=True)

@st.cache_resource
def load_bert():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
    return tokenizer, model

def get_bert_embedding(tokenizer, model, sentence, target_word):
    inputs = tokenizer(sentence, return_tensors='pt')
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    hidden_states = outputs.hidden_states[-1]
    
    target_indices = []
    target_word_lower = target_word.lower()
    
    for idx, token in enumerate(tokens):
        if target_word_lower in token.lower() and token not in ['[CLS]', '[SEP]']:
            target_indices.append(idx)
    
    if target_indices:
        embedding = hidden_states[0][target_indices].mean(dim=0).numpy()
        return embedding, tokens
    else:
        return hidden_states[0][1:-1].mean(dim=0).numpy(), tokens

def extract_ner_entities(sentence):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    chunks = ne_chunk(tagged)
    
    entities = {'GPE': [], 'DATE': [], 'TIME': [], 'ORG': [], 'PERSON': []}
    
    for chunk in chunks:
        if isinstance(chunk, Tree):
            entity_text = ' '.join([token for token, pos in chunk.leaves()])
            entity_label = chunk.label()
            if entity_label in entities:
                entities[entity_label].append(entity_text)
            elif entity_label == 'LOCATION':
                entities['GPE'].append(entity_text)
    
    return entities

def extract_srl_nltk(sentence):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    
    predicate = None
    a0 = None
    a1 = None
    am_loc = None
    am_tmp = None
    
    for i, (word, tag) in enumerate(tagged):
        if tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            if predicate is None:
                predicate = word
    
    for i, (word, tag) in enumerate(tagged):
        if tag in ['NNP', 'NN', 'PRP']:
            if i > 0 and tagged[i-1][1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                a1 = word
            elif i < len(tagged) - 1:
                next_word, next_tag = tagged[i+1]
                if next_tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                    a0 = word
    
    entities = extract_ner_entities(sentence)
    
    if entities['GPE']:
        am_loc = entities['GPE'][0]
    if entities['DATE']:
        am_tmp = entities['DATE'][0]
    elif entities['TIME']:
        am_tmp = entities['TIME'][0]
    
    prep_pattern = re.search(r'\b(in|at|on|by|near)\s+(\w+)', sentence.lower())
    if prep_pattern and not am_loc:
        am_loc = prep_pattern.group(2).capitalize()
    
    time_pattern = re.search(r'\b(this|last|next)\s+(year|month|week|day)\b', sentence.lower())
    if time_pattern and not am_tmp:
        am_tmp = time_pattern.group(0)
    
    return {
        'A0 (Agent)': a0 if a0 else '-',
        'Predicate': predicate if predicate else '-',
        'A1 (Patient)': a1 if a1 else '-',
        'AM-LOC': am_loc if am_loc else '-',
        'AM-TMP': am_tmp if am_tmp else '-'
    }

def get_pos_table(sentence):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    return [{'Token': w, 'POS': t} for w, t in tagged]

def main():
    st.set_page_config(page_title='NLP Demo', page_icon='🧠', layout='wide')
    
    st.title('🧠 自然语言处理演示系统')
    st.markdown('---')
    
    tab1, tab2 = st.tabs(['📚 词义消歧 (WSD)', '🎭 语义角色标注 (SRL)'])
    
    with tab1:
        st.header('词义消歧 (Word Sense Disambiguation)')
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader('输入')
            sentence1 = st.text_area('句子1 (含多义词)', 
                                    'I went to the bank to deposit my money.',
                                    height=80, key='s1')
            target_word = st.text_input('目标多义词', 'bank', key='target')
            sentence2 = st.text_area('句子2 (对比句子)', 
                                    'I sat by the river bank.',
                                    height=80, key='s2')
            
            if st.button('🔍 分析', key='analyze_wsd'):
                with st.spinner('加载模型中...'):
                    tokenizer, model = load_bert()
                
                st.subheader('📊 分析结果')
                
                with st.spinner('Lesk算法分析中...'):
                    tokens = word_tokenize(sentence1)
                    synset = lesk(tokens, target_word)
                    
                    if synset:
                        st.markdown(f"**Lesk算法预测:** `{synset.name()}`")
                        st.markdown(f"**词义定义:** {synset.definition()}")
                        st.markdown(f"**示例:** {', '.join(synset.examples()[:2]) if synset.examples() else '无'}")
                    else:
                        st.warning('无法确定词义')
                
                st.markdown('---')
                st.subheader('🔢 BERT词向量对比')
                
                with st.spinner('提取BERT词向量中...'):
                    emb1, tokens1 = get_bert_embedding(tokenizer, model, sentence1, target_word)
                    emb2, tokens2 = get_bert_embedding(tokenizer, model, sentence2, target_word)
                    
                    similarity = cosine_similarity([emb1], [emb2])[0][0]
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**句子1 tokens:** `{tokens1}`")
                        st.markdown(f"**向量维度:** `{emb1.shape}`")
                    with col_b:
                        st.markdown(f"**句子2 tokens:** `{tokens2}`")
                        st.markdown(f"**向量维度:** `{emb2.shape}`")
                    
                    st.metric('余弦相似度', f'{similarity:.4f}')
                    
                    if similarity > 0.8:
                        st.success('✅ 高相似度：两个句子中目标词的含义可能相同')
                    elif similarity > 0.5:
                        st.info('ℹ️ 中等相似度：目标词的含义有一定关联')
                    else:
                        st.warning('⚠️ 低相似度：两个句子中目标词可能有不同含义')
    
    with tab2:
        st.header('语义角色标注 (Semantic Role Labeling)')
        st.info('💡 使用NLTK进行词性标注和命名实体识别，通过启发式规则提取语义角色')
        
        sentence_srl = st.text_area('输入句子', 
                                   'Apple is manufacturing new smartphones in China this year.',
                                   height=80, key='srl_input')
        
        if st.button('🎯 分析语义角色', key='analyze_srl'):
            st.subheader('📋 语义角色表格')
            
            srl_result = extract_srl_nltk(sentence_srl)
            
            table_data = {
                '角色': ['A0 (施事者)', 'Predicate (谓词)', 'A1 (受事者)', 'AM-LOC (地点)', 'AM-TMP (时间)'],
                '词语': [srl_result['A0 (Agent)'], srl_result['Predicate'], 
                       srl_result['A1 (Patient)'], srl_result['AM-LOC'], srl_result['AM-TMP']]
            }
            
            st.table(table_data)
            
            st.subheader('📊 词性标注结果')
            
            tokens = word_tokenize(sentence_srl)
            tagged = pos_tag(tokens)
            
            pos_data = []
            for word, tag in tagged:
                pos_data.append({
                    'Token': word,
                    'POS': tag,
                    'Type': '动词' if tag.startswith('VB') else '名词' if tag.startswith('NN') else '形容词' if tag.startswith('JJ') else '其他'
                })
            st.table(pos_data)
            
            st.subheader('📍 命名实体识别')
            
            entities = extract_ner_entities(sentence_srl)
            ner_data = []
            for entity_type, values in entities.items():
                if values:
                    for v in values:
                        ner_data.append({'类型': entity_type, '实体': v})
            if ner_data:
                st.table(ner_data)
            else:
                st.info('未识别到命名实体')

if __name__ == '__main__':
    main()
