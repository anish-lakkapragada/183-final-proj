from sentence_transformers import SentenceTransformer, util
import re 

model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 

def preprocess_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower().strip()

def is_comment_off_topic(post_content, comment_text, threshold=0.3):
    post_content = preprocess_text(post_content)
    comment_text = preprocess_text(comment_text)
    
    post_embedding = model.encode(post_content, convert_to_tensor=True)
    comment_embedding = model.encode(comment_text, convert_to_tensor=True)
    
    similarity = util.pytorch_cos_sim(post_embedding, comment_embedding).item()

    return similarity < threshold, similarity
