from utils import parse_args, scrape_ithome_news

from BCEmbedding import EmbeddingModel
from BCEmbedding import RerankerModel

from sklearn.neighbors import KDTree
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
from tqdm import tqdm
   
class TinyVectorDB:
    def __init__(self):
        self.all_documents = {}
        self.documents = []
        self.document_embeddings = []
    
    # function for building KD-tree
    def _build_index(self):
        start_time = time.time()  
        self.kd_tree = KDTree(np.array(self.document_embeddings))
        end_time = time.time()
        self.building_time_kd = end_time - start_time
        print('\nFinish building KD-Tree, elapsed time = ', self.building_time_kd, 'sec')
        
    def insert(self, document_info_list):
        """
        Insert a list of document information into the vector database.
        
        Args:
        documents (List[Dict[str, Union[str, List[float]]]]): A list of dictionaries containing
        document information. Each dictionary should have two keys:
        - 'document': a string representing the document content
        - 'embedding': a list of floats representing the embedding (float vector) of the document.

        Returns:
        None
        """
        print('Start saving documents embeddings into database...')
        for doc_info in document_info_list:
            document = doc_info['document']
            embedding = doc_info['embedding']
            self.all_documents[document] = embedding
            self.documents.append(document)
            self.document_embeddings.append(embedding[0])
        
        self._build_index()

    def search(self, query_embedding, limit=10):
        """
        Search for similar documents based on the provided query embedding list from a vector database
        and return a limited number of results.

        Args:
        query_embedding_list (List[List[float]]): A list of lists containing query embedding vectors.
        Each inner list represents the embedding (float vector) of a query document
        limit (int): The maximum number of similar documents to return.


        Returns:
        List[List[Tuple[float, str]]]: A list of lists of tuples containing the similarity score
        and the corresponding document found in the database. Each inner list represents
        the results for a single query embedding list. Each tuple contains:
        - The similarity score (float).
        - The document (str).
        """
        
        print('Using different method to search best matching results...')
        
        # Using KD-Tree searching method
        start_time = time.time()
        kd_search_result = []
        for i in range(len(query_embedding)):
            # return top matching document indices
            distances, indices = self.kd_tree.query(np.array(query_embedding[i]), k=limit)
            result = []
            for j in range(limit):
                similarity_score = cosine_similarity(query_embedding[i], [self.document_embeddings[indices[i][j]]])[0][0]
                document = self.documents[indices[i][j]]
                result.append((document, similarity_score))
            kd_search_result.append(result)            
        end_time = time.time()
        execution_time_kd = end_time - start_time      

        # Using brute-force searching method
        start_time = time.time()        
        brute_search_result = []
        for i in range(len(query_embedding)):
            similarities = {}
            for doc, embedding in self.all_documents.items():
                similarity = cosine_similarity(query_embedding[i], embedding)
                similarities[doc] = similarity.item()

            sorted_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            brute_search_result.append(sorted_docs[:limit])
            
        end_time = time.time()
        execution_time_brute = end_time - start_time

        print('\nShowing search results and elapsed time of different methods...')
        for i in range(len(query_embedding)):
            print('\n-> KD-Tree result <-')
            for j, kd_result in enumerate(kd_search_result[i]):   
                print('=== Top {} result ==='.format(str(j+1)))             
                print('Similarity: {}'.format(kd_result[1]))
                print(kd_result[0])
                    
        for i in range(len(query_embedding)):
            print('\n -> Brute-force result <-')
            for j, brute_result in enumerate(brute_search_result[i]):   
                print('=== Top {} result ==='.format(str(j+1)))             
                print('Similarity: {}'.format(brute_result[1]))
                print(brute_result[0])
                
        print('\nKDTree search! Elapsed time: ', execution_time_kd + self.building_time_kd, 'seconds')  
        print('Greedy search! Elapsed time: ', execution_time_brute, 'seconds')                
        print('Efficieny has been improved by ', ((execution_time_brute-execution_time_kd) / execution_time_brute)*100, '%\n')  

        return kd_search_result, brute_search_result

if __name__ == "__main__":
    opt = parse_args()
    
    db = TinyVectorDB()    

    model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1")
    
    all_article_info = scrape_ithome_news(opt.num_articles) # return a dict that contains URL, titles and content
    all_document = all_article_info['Content']   

    print('Start converting article contents into embedding...')
    insert_content = []    
    for document in tqdm(all_document):
        dict_temp = {}
        dict_temp['document'] = document
        dict_temp['embedding'] = model.encode(document, enable_tqdm=False)
        insert_content.append(dict_temp)
    
    db.insert(insert_content) # insert processed document dict into database
    
    # get query sentence and corresponding embedding
    
    # Case I: query sentence is passed through command line 
    if opt.query_sentence != '':
        query = opt.query_sentence 
        query_embedding = model.encode(query, enable_tqdm=False)   
        
        similar_documents = db.search([query_embedding], limit=opt.limit)
        all_kd_result, all_greedy_result = similar_documents

    # Case II: query sentence is determined by keyboard input of user inside the program
    else:
        user_input = input("\nPlease enter your query sentence (enter 'exit' if you want to terminate the program): ")
        
        while user_input != 'exit':            
            query_embedding = model.encode(user_input, enable_tqdm=False) 
            similar_documents = db.search([query_embedding], limit=opt.limit)        
            all_kd_result, all_greedy_result = similar_documents
            user_input = input("\nPlease enter your query sentence (enter 'exit' if you want to terminate the program): ")
        
        print('Program terminating...')
                
