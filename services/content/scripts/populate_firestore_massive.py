#!/usr/bin/env python3
"""
Script para população massiva do Firestore com dados da EvolveYou
Autor: MANUS IA - Agente Especializado em Dados
Data: $(date)
"""

import json
import csv
import os
import sys
from typing import Dict, List, Any
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

class FirestorePopulator:
    def __init__(self, project_id: str = "evolveyou-23580"):
        """Inicializar conexão com Firestore"""
        self.project_id = project_id
        self.db = None
        self.batch_size = 500  # Firestore batch limit
        
    def initialize_firebase(self):
        """Inicializar Firebase Admin SDK"""
        try:
            # Tentar usar credenciais padrão do ambiente
            if not firebase_admin._apps:
                # Para ambiente de produção, usar credenciais padrão
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            print(f"✅ Conectado ao Firestore - Projeto: {self.project_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar com Firestore: {e}")
            return False
    
    def load_data_from_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Carregar dados do CSV gerado pelos agentes"""
        data = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row.get('Error'):  # Pular linhas com erro
                        continue
                        
                    try:
                        # Parse do documento JSON
                        firestore_doc = json.loads(row['Documento Firestore'])
                        
                        # Adicionar metadados
                        firestore_doc['category'] = row['Categoria']
                        firestore_doc['details'] = row['Detalhes']
                        firestore_doc['tags'] = row['Tags'].split(', ') if row['Tags'] else []
                        firestore_doc['level'] = int(row['Nível']) if row['Nível'].isdigit() else 1
                        firestore_doc['created_at'] = datetime.now()
                        firestore_doc['updated_at'] = datetime.now()
                        firestore_doc['active'] = True
                        
                        data.append(firestore_doc)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Erro ao fazer parse do JSON: {e}")
                        continue
                        
            print(f"✅ Carregados {len(data)} documentos do CSV")
            return data
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            return []
    
    def categorize_data(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorizar dados por coleção"""
        categorized = {
            'foods': [],
            'exercises': [],
            'therapies': [],
            'supplements': []
        }
        
        for item in data:
            category = item.get('category', '').lower()
            
            if 'food' in category or 'alimento' in category:
                categorized['foods'].append(item)
            elif 'exercise' in category or 'exercício' in category or 'exercicio' in category:
                categorized['exercises'].append(item)
            elif 'therapy' in category or 'terapia' in category:
                categorized['therapies'].append(item)
            elif 'supplement' in category or 'suplemento' in category:
                categorized['supplements'].append(item)
            else:
                # Tentar categorizar por nome/tags
                name = item.get('name', '').lower()
                tags = [tag.lower() for tag in item.get('tags', [])]
                
                if any(word in name for word in ['fruta', 'vegetal', 'carne', 'peixe', 'leite', 'queijo']):
                    categorized['foods'].append(item)
                elif any(word in name for word in ['supino', 'agachamento', 'corrida', 'flexão', 'rosca']):
                    categorized['exercises'].append(item)
                elif any(word in name for word in ['terapia', 'massagem', 'yoga', 'meditação']):
                    categorized['therapies'].append(item)
                else:
                    # Default para foods se não conseguir categorizar
                    categorized['foods'].append(item)
        
        return categorized
    
    def insert_batch(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Inserir documentos em lote"""
        try:
            batch = self.db.batch()
            collection_ref = self.db.collection(collection_name)
            
            for doc in documents:
                doc_ref = collection_ref.document()  # Auto-generate ID
                batch.set(doc_ref, doc)
            
            batch.commit()
            print(f"✅ Inseridos {len(documents)} documentos na coleção '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inserir lote na coleção '{collection_name}': {e}")
            return False
    
    def populate_collection(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Popular uma coleção com documentos"""
        if not documents:
            print(f"⚠️  Nenhum documento para inserir na coleção '{collection_name}'")
            return True
        
        print(f"📦 Populando coleção '{collection_name}' com {len(documents)} documentos...")
        
        # Dividir em lotes
        success_count = 0
        for i in range(0, len(documents), self.batch_size):
            batch_docs = documents[i:i + self.batch_size]
            
            if self.insert_batch(collection_name, batch_docs):
                success_count += len(batch_docs)
            
            # Pequena pausa entre lotes para evitar rate limiting
            time.sleep(0.1)
        
        print(f"✅ Coleção '{collection_name}' populada: {success_count}/{len(documents)} documentos")
        return success_count == len(documents)
    
    def populate_all(self, csv_path: str) -> bool:
        """Popular todas as coleções"""
        print("🚀 Iniciando população massiva do Firestore...")
        
        # Inicializar Firebase
        if not self.initialize_firebase():
            return False
        
        # Carregar dados
        data = self.load_data_from_csv(csv_path)
        if not data:
            print("❌ Nenhum dado carregado")
            return False
        
        # Categorizar dados
        categorized_data = self.categorize_data(data)
        
        # Popular cada coleção
        success = True
        for collection_name, documents in categorized_data.items():
            if not self.populate_collection(collection_name, documents):
                success = False
        
        # Relatório final
        print("\n🎉 POPULAÇÃO CONCLUÍDA!")
        print("=" * 50)
        for collection_name, documents in categorized_data.items():
            print(f"📊 {collection_name}: {len(documents)} documentos")
        
        total_docs = sum(len(docs) for docs in categorized_data.values())
        print(f"📈 Total: {total_docs} documentos inseridos")
        
        return success

def main():
    """Função principal"""
    # Caminho para o CSV gerado pelos agentes
    csv_path = "/home/ubuntu/populate_firestore_database.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        sys.exit(1)
    
    # Criar populador e executar
    populator = FirestorePopulator()
    
    if populator.populate_all(csv_path):
        print("✅ População massiva concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Erro durante a população")
        sys.exit(1)

if __name__ == "__main__":
    main()

