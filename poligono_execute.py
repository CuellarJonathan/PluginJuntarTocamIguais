from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields, QgsVectorFileWriter, QgsWkbTypes, QgsApplication, QgsProject, QgsProcessing
import processing

# Carregar a camada vetorial
#caminho_camada = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/poligonos.shp'
#nome_camada = 'poligonos'
#camada = QgsVectorLayer(caminho_camada, nome_camada, 'ogr')

nome_camada = "poligonos"
camada_aberta = QgsProject.instance().mapLayersByName(nome_camada)
if camada_aberta:
    camada = camada_aberta[0]  # Use a primeira camada encontrada com o nome especificado
    print(f"Nome da camada: {camada.name()}, Fonte: {camada.source()}")
else:
    print(f"Camada com o nome '{nome_camada}' não encontrada.")

# Verificar se a camada foi carregada corretamente
if not camada.isValid():
    print("Não foi possível carregar a camada vetorial!")
else:
    # Variável com todos os valores para 'densidade'
    densidades = [
        'Densa','Pouco densa','Loteamento vazio'
    ]
    # Variável com todos os valores para 'tipo'
    tipos = [
        'Área Urbanizada','Outros equipamentos urbanos','Vazio intraurbano','Loteamento vazio'
    ]
    # Variável com todos os valores para 'comparacao'
    comparacoes = [
        'Adição','Densificação','Reclassificado','Sem alteração','Adição de loteamento vazio','Adição em loteamento vazio','Subtração de loteamento vazio','Subtração','Exclusão','Desdensificação','Não mapeado'
    ]
    count_times = 0
    for densidade in densidades:
        for tipo in tipos:
            for comparacao in comparacoes:
                # Contagem
                count_times = count_times + 1
                print(f"Contagem: {count_times}")
                
                # Expressão de seleção
                expressao = "Densidade = '"+densidade+"' AND Tipo = '"+tipo+"' AND Comparacao = '"+comparacao+"'"
                print(f"Expressão: {expressao}")

                # Selecionar os polígonos que atendem à expressão
                camada.selectByExpression(expressao)

                # Obter somente as feições selecionadas
                feicoes_selecionadas = camada.selectedFeatures()

                if feicoes_selecionadas:
                    print(f"Número de polígonos selecionados: {len(feicoes_selecionadas)}")
                    
                    # Obter somente os IDs das feições selecionadas
                    ids_selecionados = [f.id() for f in feicoes_selecionadas]

                    # Criar cópia temporária das feições selecionadas para evitar alterações na camada original
                    #camada_temporaria = QgsVectorLayer("Polygon?crs=EPSG:4674", "CamadaTemporaria", "memory")
                    #camada_temporaria.startEditing()
                    #for feicao in feicoes_selecionadas:
                    #    nova_feicao = QgsFeature(feicao)
                    #    camada_temporaria.addFeature(nova_feicao)
                    #camada_temporaria.commitChanges()

                    #resultado_join = processing.run("qgis:joinbylocationsummary", {
                    #    'INPUT': camada,
                    #    'PREDICATE': [3],
                    #    'JOIN': camada,
                    #    'JOIN_FIELDS': ['id', 'Densidade', 'Tipo', 'Comparacao'],
                    #    'SUMMARIES': [0],
                    #    'DISCARD_NONMATCHING': False,
                    #    'OUTPUT': 'TEMPORARY_OUTPUT'
                    #})
                    
                    #caminho_saida_join = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/temp_join.shp'
                    resultado_join = processing.run("qgis:joinbylocationsummary", {
                       'INPUT':QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True),
                       'PREDICATE':[3],
                       'JOIN':QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True),
                       'JOIN_FIELDS':[],
                       'SUMMARIES':[0],
                       'DISCARD_NONMATCHING':False,
                       'OUTPUT': 'TEMPORARY_OUTPUT'
                    })
                    
                    # caminho_saida_join = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/temp_join.shp'
                    # resultado_join = processing.run("qgis:joinbylocationsummary", {
                        # 'INPUT': camada,
                        # 'PREDICATE': [3],
                        # 'JOIN': camada,
                        # 'JOIN_FIELDS': ['id', 'Densidade', 'Tipo', 'Comparacao'],
                        # 'SUMMARIES': [0],
                        # 'DISCARD_NONMATCHING': False,
                        # 'INPUT_SELECTION': ids_selecionados,
                        # 'JOIN_SELECTION': ids_selecionados,
                        # 'OUTPUT': caminho_saida_join
                    # })

                    if 'OUTPUT' in resultado_join:
                        caminho_temporario_saida = resultado_join['OUTPUT']
                        #caminho_saida_dissolve = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/temp_dissolve.shp'
                        resultado_dissolve = processing.run("native:dissolve", {
                            'INPUT': caminho_temporario_saida,
                            'FIELD': [],  # Dissolver com base nos campos
                            'SEPARATE_DISJOINT': False,
                            'OUTPUT': 'TEMPORARY_OUTPUT'
                        })

                        if 'OUTPUT' in resultado_dissolve:
                            caminho_temporario_saida_dissolve = resultado_dissolve['OUTPUT']
                            caminho_saida_multipart = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/Poligonos/poligonos_'+densidade+'_'+tipo+'_'+comparacao+'.shp'
                            resultado_multipart = processing.run("native:multiparttosingleparts", {
                                'INPUT': caminho_temporario_saida_dissolve,
                                'OUTPUT': caminho_saida_multipart
                            })

                            if 'OUTPUT' in resultado_multipart:
                                caminho_temporario_saida_multipart = resultado_multipart['OUTPUT']
                                
                                nome_camada_multipart = 'poligonos_'+densidade+'_'+tipo+'_'+comparacao
                                nova_camada = QgsVectorLayer(caminho_temporario_saida_multipart, nome_camada_multipart, "ogr")
                                if not nova_camada.isValid():
                                    print("Erro ao carregar a camada resultante.")
                                else:
                                    QgsProject.instance().addMapLayer(nova_camada)
                                    print("Processamento concluído com sucesso.")
                            else:
                                print("Erro ao executar o algoritmo de dividir (multiparttosingleparts).")
                        else:
                            print("Erro ao executar o algoritmo de dissolver.")
                    else:
                        print("Erro ao executar o algoritmo de junção.")

                else:
                    print("Nenhum polígono selecionado.")
