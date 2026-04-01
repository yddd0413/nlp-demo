import streamlit as st
import nltk
from nltk.wsd import lesk
from nltk.corpus import wordnet
import spacy
from spacy import displacy
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

@st.cache_resource
def load_bert():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
    return tokenizer, model

@st.cache_resource
def load_spacy():
    return spacy.load('en_core_web_sm')

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

def extract_srl(doc):
    predicate = None
    a0 = None
    a1 = None
    am_loc = None
    am_tmp = None
    
    for token in doc:
        if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
            predicate = token.text
            break
        elif token.dep_ == 'ROOT':
            predicate = token.text
    
    for token in doc:
        if token.dep_ == 'nsubj' and predicate:
            a0 = token.text
        
        if token.dep_ == 'dobj' and predicate:
            a1 = token.text
        
        if token.dep_ == 'prep':
            for child in token.children:
                if child.dep_ == 'pobj':
                    if token.text.lower() in ['in', 'at', 'on', 'by', 'near']:
                        am_loc = child.text
                    elif token.text.lower() in ['during', 'before', 'after']:
                        am_tmp = child.text
        
        if token.ent_type_ == 'GPE' and not am_loc:
            am_loc = token.text
        
        if token.ent_type_ in ['DATE', 'TIME'] and not am_tmp:
            am_tmp = token.text
    
    return {
        'A0 (Agent)': a0 if a0 else '-',
        'Predicate': predicate if predicate else '-',
        'A1 (Patient)': a1 if a1 else '-',
        'AM-LOC': am_loc if am_loc else '-',
        'AM-TMP': am_tmp if am_tmp else '-'
    }

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
                    tokens = nltk.word_tokenize(sentence1)
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
        
        sentence_srl = st.text_area('输入句子', 
                                   'Apple is manufacturing new smartphones in China this year.',
                                   height=80, key='srl_input')
        
        if st.button('🎯 分析语义角色', key='analyze_srl'):
            nlp = load_spacy()
            doc = nlp(sentence_srl)
            
            st.subheader('📋 语义角色表格')
            
            srl_result = extract_srl(doc)
            
            col_widths = [1, 1, 1, 1, 1]
            
            table_data = {
                '角色': ['A0 (施事者)', 'Predicate (谓词)', 'A1 (受事者)', 'AM-LOC (地点)', 'AM-TMP (时间)'],
                '词语': [srl_result['A0 (Agent)'], srl_result['Predicate'], 
                       srl_result['A1 (Patient)'], srl_result['AM-LOC'], srl_result['AM-TMP']]
            }
            
            st.table(table_data)
            
            st.subheader('📊 依存句法分析图')
            
            options = {'compact': True, 'bg': '#f0f0f5', 'color': '#333', 'font': 'Arial'}
            html = displacy.render(doc, style='dep', options=options)
            st.components.v1.html(html, height=300, scrolling=True)
            
            with st.expander('📝 查看详细依存关系'):
                dep_data = []
                for token in doc:
                    dep_data.append({
                        'Token': token.text,
                        'Lemma': token.lemma_,
                        'POS': token.pos_,
                        'Dep': token.dep_,
                        'Head': token.head.text
                    })
                st.table(dep_data)

if __name__ == '__main__':
    main()
