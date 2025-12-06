from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from products.models import Product

def ai_suggestions(product):
    all_products = Product.objects.exclude(user=product.user)
    if not all_products:
        return []

    # Combine title + tags
    corpus = [p.title + " " + (p.tags or "") for p in all_products]
    
    # Convert text to vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus + [product.title + " " + (product.tags or "")])
    
    # Compute similarity
    similarity = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    
    # Sort products by similarity (convert indices to int)
    sorted_products = [all_products[int(i)] for i in similarity.argsort()[::-1]]
    
    # Return top 10
    return sorted_products[:10]
