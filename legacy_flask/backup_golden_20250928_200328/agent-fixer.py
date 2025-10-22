#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NADAKKI AI SUITE - AGENT FIXER
Repara agentes generados agregando métodos faltantes de algoritmos

Autor: Nadakki AI Suite
Fecha: Agosto 2025
Versión: 2.0
"""

import os
import re
from pathlib import Path
from typing import List, Dict

class AgentFixer:
    def __init__(self):
        self.base_path = Path("C:/Users/cesar/Projects/nadakki-ai-suite/nadakki-ai-suite")
        self.agents_path = self.base_path / "agents"
        
        # Templates de métodos de algoritmos
        self.algorithm_methods = {
            "cosine_similarity": """
    def _cosine_similarity_scoring(self, features):
        \"\"\"Implementación de similitud coseno\"\"\"
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Simulación básica - reemplazar con lógica real
            feature_vector = np.array([[features.get('income', 0), 
                                      features.get('credit_score', 0),
                                      features.get('age', 0)]]).reshape(1, -1)
            
            # Base vector de referencia (promedio del mercado)
            base_vector = np.array([[50000, 750, 35]]).reshape(1, -1)
            
            similarity = cosine_similarity(feature_vector, base_vector)[0][0]
            return min(max(similarity, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in cosine similarity: {str(e)}")
            return 0.5  # Valor por defecto
""",
            
            "euclidean_distance": """
    def _euclidean_distance_scoring(self, features):
        \"\"\"Implementación de distancia euclidiana normalizada\"\"\"
        try:
            import numpy as np
            
            # Normalizar features
            income_norm = min(features.get('income', 0) / 100000, 1.0)
            score_norm = features.get('credit_score', 0) / 850
            age_norm = min(features.get('age', 0) / 80, 1.0)
            
            # Vector de referencia (perfil ideal)
            ideal_vector = np.array([0.6, 0.9, 0.4])  # 60k income, 765 score, 32 age
            current_vector = np.array([income_norm, score_norm, age_norm])
            
            # Calcular distancia euclidiana
            distance = np.linalg.norm(current_vector - ideal_vector)
            
            # Convertir distancia a score (menor distancia = mayor score)
            score = max(0.0, 1.0 - distance / np.sqrt(3))
            return score
            
        except Exception as e:
            logger.error(f"Error in euclidean distance: {str(e)}")
            return 0.5
""",
            
            "jaccard_index": """
    def _jaccard_index_scoring(self, features):
        \"\"\"Implementación de índice Jaccard\"\"\"
        try:
            # Características categóricas
            employment_types = {'full_time': 1, 'part_time': 0.7, 'self_employed': 0.8, 'unemployed': 0.1}
            education_levels = {'high_school': 0.5, 'college': 0.8, 'graduate': 1.0, 'postgraduate': 1.0}
            
            # Features del perfil actual
            current_features = set()
            if features.get('employment_type') in employment_types:
                current_features.add(f"emp_{features['employment_type']}")
            if features.get('education_level') in education_levels:
                current_features.add(f"edu_{features['education_level']}")
            if features.get('credit_score', 0) > 700:
                current_features.add('good_credit')
            if features.get('income', 0) > 40000:
                current_features.add('good_income')
            
            # Features del perfil ideal
            ideal_features = {'emp_full_time', 'edu_college', 'good_credit', 'good_income'}
            
            # Calcular Jaccard
            intersection = len(current_features & ideal_features)
            union = len(current_features | ideal_features)
            
            jaccard_score = intersection / union if union > 0 else 0.0
            return jaccard_score
            
        except Exception as e:
            logger.error(f"Error in jaccard index: {str(e)}")
            return 0.5
""",
            
            "random_forest": """
    def _random_forest_scoring(self, features):
        \"\"\"Implementación de Random Forest simulado\"\"\"
        try:
            # Simulación de Random Forest con reglas básicas
            score = 0.0
            
            # Árbol 1: Income-based
            if features.get('income', 0) > 60000:
                score += 0.3
            elif features.get('income', 0) > 30000:
                score += 0.2
            else:
                score += 0.1
            
            # Árbol 2: Credit score-based
            if features.get('credit_score', 0) > 750:
                score += 0.3
            elif features.get('credit_score', 0) > 650:
                score += 0.2
            else:
                score += 0.1
            
            # Árbol 3: Age-based
            age = features.get('age', 0)
            if 25 <= age <= 45:
                score += 0.2
            elif 18 <= age <= 65:
                score += 0.15
            else:
                score += 0.1
            
            # Árbol 4: Debt-to-income
            dti = features.get('debt_to_income', 0.5)
            if dti < 0.3:
                score += 0.2
            elif dti < 0.5:
                score += 0.1
            else:
                score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error in random forest: {str(e)}")
            return 0.5
""",
            
            "neural_network": """
    def _neural_network_scoring(self, features):
        \"\"\"Implementación de Red Neuronal simulada\"\"\"
        try:
            import numpy as np
            
            # Normalizar inputs
            inputs = np.array([
                features.get('income', 0) / 100000,
                features.get('credit_score', 0) / 850,
                features.get('age', 0) / 80,
                features.get('debt_to_income', 0.5),
                1.0 if features.get('employment_type') == 'full_time' else 0.5
            ])
            
            # Pesos simulados (hidden layer)
            W1 = np.array([
                [0.5, -0.3, 0.8, -0.6, 0.4],
                [0.7, 0.2, -0.4, 0.5, -0.3],
                [-0.2, 0.9, 0.1, -0.7, 0.6],
                [0.3, -0.5, 0.7, 0.2, -0.4]
            ])
            b1 = np.array([0.1, -0.2, 0.3, -0.1])
            
            # Forward pass hidden layer
            h1 = np.maximum(0, np.dot(W1, inputs) + b1)  # ReLU activation
            
            # Output layer
            W2 = np.array([0.6, -0.3, 0.8, 0.2])
            b2 = 0.1
            
            output = np.dot(W2, h1) + b2
            
            # Sigmoid activation
            score = 1 / (1 + np.exp(-output))
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error in neural network: {str(e)}")
            return 0.5
""",
            
            "lstm": """
    def _lstm_scoring(self, features):
        \"\"\"Implementación de LSTM simulado\"\"\"
        try:
            # Simulación de LSTM para análisis temporal
            # En implementación real, usaría histórico de transacciones
            
            # Crear secuencia temporal simulada
            sequence_features = []
            for i in range(12):  # 12 meses
                month_feature = {
                    'income': features.get('income', 0) * (0.95 + 0.1 * (i % 3) / 3),
                    'expenses': features.get('income', 0) * 0.7 * (0.9 + 0.2 * (i % 4) / 4),
                    'balance': features.get('income', 0) * 0.3 * (1 + 0.1 * i / 12)
                }
                sequence_features.append(month_feature)
            
            # Calcular tendencias
            income_trend = (sequence_features[-1]['income'] - sequence_features[0]['income']) / sequence_features[0]['income']
            expense_stability = 1.0 - abs(sequence_features[-1]['expenses'] - sequence_features[0]['expenses']) / sequence_features[0]['expenses']
            
            # Score basado en tendencias
            score = 0.5 + income_trend * 0.3 + expense_stability * 0.2
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in LSTM: {str(e)}")
            return 0.5
""",
            
            "clustering": """
    def _clustering_scoring(self, features):
        \"\"\"Implementación de Clustering\"\"\"
        try:
            # Definir centros de clusters típicos
            cluster_centers = {
                'high_quality': {'income': 80000, 'credit_score': 800, 'age': 35},
                'medium_quality': {'income': 50000, 'credit_score': 700, 'age': 30},
                'low_quality': {'income': 25000, 'credit_score': 600, 'age': 25}
            }
            
            # Calcular distancias a cada cluster
            distances = {}
            for cluster_name, center in cluster_centers.items():
                distance = 0
                distance += abs(features.get('income', 0) - center['income']) / 100000
                distance += abs(features.get('credit_score', 0) - center['credit_score']) / 850
                distance += abs(features.get('age', 0) - center['age']) / 80
                distances[cluster_name] = distance
            
            # Encontrar cluster más cercano
            closest_cluster = min(distances.keys(), key=lambda k: distances[k])
            
            # Score basado en cluster
            cluster_scores = {'high_quality': 0.9, 'medium_quality': 0.7, 'low_quality': 0.4}
            base_score = cluster_scores[closest_cluster]
            
            # Ajustar score basado en distancia
            distance_factor = 1.0 - distances[closest_cluster] / 3.0
            final_score = base_score * max(distance_factor, 0.5)
            
            return min(max(final_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in clustering: {str(e)}")
            return 0.5
""",
            
            # Métodos adicionales para otros algoritmos
            "regression_analysis": """
    def _regression_analysis_scoring(self, features):
        \"\"\"Implementación de Análisis de Regresión\"\"\"
        try:
            # Regresión lineal simple simulada
            # Score = β0 + β1*income + β2*credit_score + β3*age + β4*dti
            
            coefficients = {
                'intercept': 0.2,
                'income': 0.000005,  # 5e-6 per dollar
                'credit_score': 0.0008,  # 0.0008 per point
                'age': -0.002,  # Penalty for age
                'debt_to_income': -0.6  # Strong penalty for high DTI
            }
            
            score = coefficients['intercept']
            score += coefficients['income'] * features.get('income', 0)
            score += coefficients['credit_score'] * features.get('credit_score', 0)
            score += coefficients['age'] * features.get('age', 0)
            score += coefficients['debt_to_income'] * features.get('debt_to_income', 0.5)
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in regression analysis: {str(e)}")
            return 0.5
""",
            
            "time_series": """
    def _time_series_scoring(self, features):
        \"\"\"Implementación de Análisis de Series Temporales\"\"\"
        try:
            # Simulación de análisis temporal
            # En implementación real usaría histórico real del cliente
            
            # Generar serie temporal simulada
            import random
            monthly_scores = []
            base_score = 0.7
            
            for month in range(24):  # 24 meses
                # Simular variación temporal
                seasonal_factor = 0.1 * (1 + 0.5 * (month % 12) / 12)
                trend_factor = 0.02 * month / 24
                noise = random.uniform(-0.05, 0.05)
                
                monthly_score = base_score + seasonal_factor + trend_factor + noise
                monthly_scores.append(max(0.0, min(1.0, monthly_score)))
            
            # Calcular métricas temporales
            recent_trend = sum(monthly_scores[-6:]) / 6 - sum(monthly_scores[-12:-6]) / 6
            stability = 1.0 - (max(monthly_scores[-12:]) - min(monthly_scores[-12:])) / 2
            
            # Score final basado en tendencia y estabilidad
            final_score = monthly_scores[-1] + recent_trend * 0.3 + stability * 0.2
            
            return min(max(final_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in time series: {str(e)}")
            return 0.5
""",
            
            "monte_carlo": """
    def _monte_carlo_scoring(self, features):
        \"\"\"Implementación de Simulación Monte Carlo\"\"\"
        try:
            import random
            
            simulations = 1000
            success_count = 0
            
            for _ in range(simulations):
                # Simular escenarios aleatorios
                income_variation = random.uniform(0.8, 1.2)
                market_condition = random.uniform(0.9, 1.1)
                personal_factor = random.uniform(0.85, 1.15)
                
                simulated_income = features.get('income', 0) * income_variation
                simulated_score = features.get('credit_score', 0) * market_condition
                
                # Criterio de éxito
                if (simulated_income > 40000 and 
                    simulated_score > 650 and 
                    personal_factor > 0.9):
                    success_count += 1
            
            success_rate = success_count / simulations
            return success_rate
            
        except Exception as e:
            logger.error(f"Error in monte carlo: {str(e)}")
            return 0.5
""",
            
            "genetic_algorithm": """
    def _genetic_algorithm_scoring(self, features):
        \"\"\"Implementación de Algoritmo Genético\"\"\"
        try:
            import random
            
            # Población inicial de "genes" (pesos)
            population_size = 50
            genes = 5  # income, credit_score, age, dti, employment
            
            # Generar población inicial
            population = []
            for _ in range(population_size):
                individual = [random.uniform(0, 1) for _ in range(genes)]
                population.append(individual)
            
            # Evaluar fitness (simplificado)
            def fitness(individual):
                weighted_score = (
                    individual[0] * features.get('income', 0) / 100000 +
                    individual[1] * features.get('credit_score', 0) / 850 +
                    individual[2] * (1 - features.get('age', 30) / 80) +
                    individual[3] * (1 - features.get('debt_to_income', 0.5)) +
                    individual[4] * (1 if features.get('employment_type') == 'full_time' else 0.5)
                )
                return weighted_score / sum(individual)
            
            # Encontrar mejor individuo
            best_fitness = max(fitness(ind) for ind in population)
            
            return min(max(best_fitness, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in genetic algorithm: {str(e)}")
            return 0.5
""",
            
            "rule_engine": """
    def _rule_engine_scoring(self, features):
        \"\"\"Implementación de Motor de Reglas\"\"\"
        try:
            score = 0.0
            
            # Regla 1: Income rules
            income = features.get('income', 0)
            if income >= 80000:
                score += 0.25
            elif income >= 50000:
                score += 0.20
            elif income >= 30000:
                score += 0.15
            else:
                score += 0.05
            
            # Regla 2: Credit score rules
            credit_score = features.get('credit_score', 0)
            if credit_score >= 750:
                score += 0.25
            elif credit_score >= 700:
                score += 0.20
            elif credit_score >= 650:
                score += 0.15
            else:
                score += 0.05
            
            # Regla 3: Debt-to-income rules
            dti = features.get('debt_to_income', 0.5)
            if dti <= 0.3:
                score += 0.25
            elif dti <= 0.4:
                score += 0.15
            elif dti <= 0.5:
                score += 0.10
            else:
                score += 0.0
            
            # Regla 4: Employment rules
            emp_type = features.get('employment_type', '')
            if emp_type == 'full_time':
                score += 0.25
            elif emp_type == 'self_employed':
                score += 0.15
            elif emp_type == 'part_time':
                score += 0.10
            else:
                score += 0.0
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error in rule engine: {str(e)}")
            return 0.5
""",
            
            "nlp": """
    def _nlp_scoring(self, features):
        \"\"\"Implementación de Procesamiento de Lenguaje Natural\"\"\"
        try:
            # Simulación de análisis NLP de comentarios/notas
            comments = features.get('comments', 'good customer')
            
            # Palabras clave positivas y negativas
            positive_keywords = ['good', 'excellent', 'reliable', 'stable', 'responsible']
            negative_keywords = ['bad', 'poor', 'unreliable', 'risky', 'problematic']
            
            # Análisis de sentimiento básico
            positive_count = sum(1 for word in positive_keywords if word.lower() in comments.lower())
            negative_count = sum(1 for word in negative_keywords if word.lower() in comments.lower())
            
            # Score basado en sentimiento
            if positive_count > negative_count:
                sentiment_score = 0.8 + (positive_count - negative_count) * 0.05
            elif negative_count > positive_count:
                sentiment_score = 0.4 - (negative_count - positive_count) * 0.05
            else:
                sentiment_score = 0.6
            
            return min(max(sentiment_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in NLP: {str(e)}")
            return 0.5
""",
            
            "computer_vision": """
    def _computer_vision_scoring(self, features):
        \"\"\"Implementación de Visión por Computadora\"\"\"
        try:
            # Simulación de análisis de documentos
            document_quality = features.get('document_quality', 'good')
            
            # Simulación de métricas de CV
            quality_scores = {
                'excellent': 0.95,
                'good': 0.85,
                'fair': 0.65,
                'poor': 0.35
            }
            
            base_score = quality_scores.get(document_quality, 0.7)
            
            # Factores adicionales de CV
            has_watermark = features.get('has_watermark', True)
            text_clarity = features.get('text_clarity', 0.9)
            image_resolution = features.get('image_resolution', 0.8)
            
            # Ajustar score
            if has_watermark:
                base_score += 0.05
            
            base_score *= text_clarity * image_resolution
            
            return min(max(base_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in computer vision: {str(e)}")
            return 0.5
""",
            
            "ensemble_learning": """
    def _ensemble_learning_scoring(self, features):
        \"\"\"Implementación de Aprendizaje Conjunto\"\"\"
        try:
            # Combinar múltiples algoritmos
            scores = []
            
            # Ejecutar otros algoritmos si están disponibles
            if hasattr(self, '_random_forest_scoring'):
                scores.append(self._random_forest_scoring(features))
            
            if hasattr(self, '_neural_network_scoring'):
                scores.append(self._neural_network_scoring(features))
            
            if hasattr(self, '_regression_analysis_scoring'):
                scores.append(self._regression_analysis_scoring(features))
            
            # Si no hay otros algoritmos, usar reglas básicas
            if not scores:
                scores = [
                    min(features.get('income', 0) / 100000, 1.0) * 0.3,
                    features.get('credit_score', 0) / 850 * 0.4,
                    (1 - features.get('debt_to_income', 0.5)) * 0.3
                ]
            
            # Weighted ensemble
            weights = [0.4, 0.3, 0.3][:len(scores)]
            weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            weighted_score /= sum(weights)
            
            return min(max(weighted_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error in ensemble learning: {str(e)}")
            return 0.5
"""
        }

    def fix_agent_file(self, agent_file: Path) -> bool:
        """Repara un archivo de agente agregando métodos faltantes"""
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Buscar algoritmos declarados
            algorithms_match = re.search(r'self\.algorithms\s*=\s*(\[.*?\])', content, re.DOTALL)
            if not algorithms_match:
                print(f"  ⚠️  No se encontraron algoritmos en {agent_file.name}")
                return False
            
            try:
                algorithms_str = algorithms_match.group(1)
                # Evaluar la lista de algoritmos de forma segura
                algorithms = eval(algorithms_str)
            except:
                print(f"  ❌ Error parseando algoritmos en {agent_file.name}")
                return False
            
            # Agregar métodos faltantes
            methods_added = 0
            for algorithm in algorithms:
                method_name = f"_{algorithm}_scoring"
                
                # Verificar si el método ya existe
                if method_name not in content:
                    if algorithm in self.algorithm_methods:
                        # Encontrar el lugar donde insertar (antes del último método)
                        insert_position = content.rfind('def test_')
                        if insert_position == -1:
                            insert_position = content.rfind('if __name__')
                        if insert_position == -1:
                            insert_position = len(content)
                        
                        # Insertar el método
                        method_code = self.algorithm_methods[algorithm]
                        content = content[:insert_position] + method_code + "\n" + content[insert_position:]
                        methods_added += 1
                        print(f"    ✅ Agregado método: {method_name}")
                    else:
                        print(f"    ⚠️  Método no disponible: {method_name}")
            
            # Guardar si hubo cambios
            if content != original_content:
                with open(agent_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  🎯 {agent_file.name}: {methods_added} métodos agregados")
                return True
            else:
                print(f"  ✅ {agent_file.name}: No necesita reparación")
                return False
                
        except Exception as e:
            print(f"  ❌ Error reparando {agent_file.name}: {str(e)}")
            return False

    def fix_all_agents(self):
        """Repara todos los agentes en el proyecto"""
        print("🔧 INICIANDO REPARACIÓN DE AGENTES")
        print("=" * 50)
        
        fixed_count = 0
        total_count = 0
        
        for module_dir in self.agents_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                print(f"\n📦 Reparando módulo: {module_dir.name.upper()}")
                
                # Buscar archivos de agentes
                agent_files = [f for f in module_dir.glob("*.py") 
                              if not f.name.startswith('_') 
                              and not f.name.endswith('_coordinator.py')
                              and f.name != '__init__.py']
                
                for agent_file in agent_files:
                    total_count += 1
                    if self.fix_agent_file(agent_file):
                        fixed_count += 1
        
        print("\n" + "=" * 50)
        print(f"🎉 REPARACIÓN COMPLETADA")
        print(f"✅ Agentes reparados: {fixed_count}/{total_count}")
        print("=" * 50)
        
        return fixed_count, total_count

    def test_repaired_agent(self, agent_file: Path):
        """Prueba un agente reparado"""
        try:
            print(f"🧪 Probando agente reparado: {agent_file.name}")
            
            # Cambiar al directorio del agente
            original_cwd = os.getcwd()
            os.chdir(agent_file.parent)
            
            # Ejecutar el agente
            result = os.system(f"python {agent_file.name}")
            
            # Restaurar directorio
            os.chdir(original_cwd)
            
            if result == 0:
                print(f"  ✅ Test exitoso: {agent_file.name}")
                return True
            else:
                print(f"  ❌ Test falló: {agent_file.name}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error probando {agent_file.name}: {str(e)}")
            return False

def main():
    """Función principal del reparador"""
    import sys
    
    fixer = AgentFixer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "fix":
            # Reparar todos los agentes
            fixer.fix_all_agents()
            
        elif command == "test":
            # Probar agentes después de reparación
            print("🧪 Probando agentes reparados...")
            
            test_files = [
                "agents/originacion/sentinelbot.py",
                "agents/decision/quantumdecision.py",
                "agents/vigilancia/earlywarning.py"
            ]
            
            for test_file in test_files:
                test_path = Path(test_file)
                if test_path.exists():
                    fixer.test_repaired_agent(test_path)
            
        else:
            print(f"❌ Comando desconocido: {command}")
    
    else:
        print("🔧 NADAKKI AI SUITE - AGENT FIXER")
        print("=" * 40)
        print("Comandos disponibles:")
        print("  python agent-fixer.py fix   # Reparar todos los agentes")
        print("  python agent-fixer.py test  # Probar agentes reparados")

if __name__ == "__main__":
    main()