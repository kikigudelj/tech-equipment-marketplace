from django.core.management.base import BaseCommand
from myapp.models import Product
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.neighbors import NearestNeighbors

class Command(BaseCommand):
    help = 'Pronađi najsličnije proizvode za preporuku'

    def recommend_similar_products(self, product_id):
        products = Product.objects.values('id', 'category', 'brand', 'price')
        product_df = pd.DataFrame(products)
        
        category_encoder = OneHotEncoder(sparse_output=False)
        brand_encoder = OneHotEncoder(sparse_output=False)
                
        category_encoded = category_encoder.fit_transform(product_df[['category']])
        brand_encoded = brand_encoder.fit_transform(product_df[['brand']])
        
        scaler = MinMaxScaler()
        price_normalized = scaler.fit_transform(product_df[['price']])
        
        features = pd.concat([
            pd.DataFrame(category_encoded, columns=category_encoder.get_feature_names_out(['category'])),
            pd.DataFrame(brand_encoded, columns=brand_encoder.get_feature_names_out(['brand'])),
            pd.DataFrame(price_normalized, columns=['price'])
        ], axis=1)

        knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
        knn.fit(features)
        
        product_index = product_df[product_df['id'] == product_id].index[0]
        distances, indices = knn.kneighbors(features.loc[[product_index]])
  
        similar_products = product_df.iloc[indices[0][1:5]]
        recommendations = similar_products[['id', 'category', 'brand', 'price']].to_dict(orient='records')

        return recommendations