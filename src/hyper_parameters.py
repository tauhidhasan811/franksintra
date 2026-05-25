params = {
    'accepted_parameters': ['temperature', 'streaming'],
    'model_name': 'gpt-4.1-2025-04-14',
    'knowledge_path': r'data\files\YoloHeat Company Guide.docx',
    'chromadb_path': r'data\chroma_db',
    'client_name': 'all_data', 
    'collections': {
        'products': {
            'exclude_field' : ['images', 'includedImages', 'featureInformation.featureLogo', 'user', 'createdAt', 'updatedAt', '__v']
        },
        'boilercontrollers': {
            'exclude_field' : []
        },
        'extras': {
            'exclude_field' : ['images', 'createdAt', 'updatedAt', '__v']
        },
        # 'services': {
        #     'exclude_field' : ['_id', 'user', 'updatedAt', '__v']
        # }
    }
    
}