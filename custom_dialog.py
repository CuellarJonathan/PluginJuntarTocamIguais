from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QComboBox, QCheckBox, QPushButton, QGroupBox
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields, QgsVectorFileWriter, QgsWkbTypes, QgsApplication, QgsProject, QgsProcessing, QgsProcessingFeatureSourceDefinition, QgsProcessingUtils
from qgis.utils import iface
import itertools
import processing

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomDialog, self).__init__(parent)
        
        # self.iface = iface
        
        self.setWindowTitle("Configurar Plugin")
        
        # Defina o tamanho da janela
        self.resize(400, 400)  # Largura: 400 pixels, Altura: 400 pixels
        
        # Obter todas as camadas abertas no projeto atual
        camadas_abertas = QgsProject.instance().mapLayers().values()
        
        camadas_names = []
        # Iterar sobre as camadas abertas
        for camada in camadas_abertas:
            # Verificar se a camada é do tipo desejado, por exemplo, camada vetorial
            if isinstance(camada, QgsVectorLayer):
                # Aqui você pode fazer qualquer operação desejada com a camada
                camadas_names.append(camada.name())
                # print(f"Nome da camada: {camada.name()}, Fonte: {camada.source()}")
        
        layout = QVBoxLayout()

        # Criar um painel (GroupBox)
        self.panel = QGroupBox("Campos")

        # Criar um layout para o painel
        self.layout_panel = QVBoxLayout()
        
        # Dropdown list
        self.dropdown = QComboBox()
        self.dropdown.addItems(camadas_names)
        layout.addWidget(self.dropdown)
        
        camada_name = self.dropdown.currentText()
        
        camada = self.openLayer(camada_name)
        campos = self.fieldsLayer(camada)
        
        # Lista de nomes dos campos
        nomes_campos = []
        for campo in campos:
            nomes_campos.append(campo.name())
        # nomes_campos = ['campo1', 'campo2', 'campo3']  # Substitua pelos nomes reais dos seus campos

        # Criar e adicionar checkboxes para cada campo
        self.checkboxes = []
        for nome_campo in nomes_campos:
            checkbox = QCheckBox(nome_campo)
            self.layout_panel.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # Definir o layout do painel
        self.panel.setLayout(self.layout_panel)

        # Adicionar o painel à janela principal do plugin
        layout.addWidget(self.panel)
        
        # Checkbox
        self.checkbox1 = QCheckBox("Unir")
        self.checkbox2 = QCheckBox("Dissolver")
        self.checkbox3 = QCheckBox("Fazer Multipartes")
        self.checkbox4 = QCheckBox("Mesclar Camadas")
        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(True)
        self.checkbox3.setChecked(True)
        self.checkbox4.setChecked(True)
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)
        layout.addWidget(self.checkbox4)
        
        # Button
        self.button = QPushButton("Executar")
        self.button.clicked.connect(self.on_button_clicked)
        self.dropdown.currentIndexChanged.connect(self.update_checkboxes)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        
    def update_checkboxes(self, index):
        # Limpar o layout do painel antes de adicionar os novos checkboxes
        # clear_layout(panel.layout())
        # Limpar o layout do painel antes de adicionar os novos checkboxes
        for i in reversed(range(self.panel.layout().count())):
            self.panel.layout().itemAt(i).widget().setParent(None)

        # Obter o valor selecionado no dropdown
        # valor_selecionado = dropdown.currentText()

        # Obter os nomes dos campos com base no valor selecionado
        # campos = obter_campos_para_combinacoes(valor_selecionado)

        # Adicionar novos checkboxes ao painel com base nos campos obtidos
        # for campo in campos:
            # checkbox = QCheckBox(campo)
            # panel.layout().addWidget(checkbox)
            
        camada_name = self.dropdown.currentText()
        
        camada = self.openLayer(camada_name)
        campos = self.fieldsLayer(camada)
        
        # Lista de nomes dos campos
        nomes_campos = []
        for campo in campos:
            nomes_campos.append(campo.name())
        # nomes_campos = ['campo1', 'campo2', 'campo3']  # Substitua pelos nomes reais dos seus campos

        # Criar e adicionar checkboxes para cada campo
        self.checkboxes = []
        for nome_campo in nomes_campos:
            checkbox = QCheckBox(nome_campo)
            self.panel.layout().addWidget(checkbox)
            self.checkboxes.append(checkbox)
    
    def on_button_clicked(self):
        dropdown_value = self.dropdown.currentText()
        checkboxes = self.checkboxes
        checkbox_state1 = self.checkbox1.isChecked()
        checkbox_state2 = self.checkbox2.isChecked()
        checkbox_state3 = self.checkbox3.isChecked()
        checkbox_state4 = self.checkbox4.isChecked()
        print("Dropdown value:", dropdown_value)
        print("Checkbox1 state:", checkbox_state1)
        print("Checkbox2 state:", checkbox_state2)
        print("Checkbox3 state:", checkbox_state3)
        print("Checkbox4 state:", checkbox_state4)
        self.executePlugin(dropdown_value, checkboxes, checkbox_state1, checkbox_state2, checkbox_state3, checkbox_state4)
    
    def openLayer(self, nome_camada):
        camada_aberta = QgsProject.instance().mapLayersByName(nome_camada)
        if camada_aberta:
            camada = camada_aberta[0]  # Use a primeira camada encontrada com o nome especificado
            print(f"Nome da camada: {camada.name()}, Fonte: {camada.source()}")
        else:
            camada = camada_aberta[0]  # Use a primeira camada encontrada com o nome especificado
            print(f"Camada com o nome '{nome_camada}' não encontrada.")
        return camada
    
    def fieldsLayer(self, layer):
        # Obter todos os campos da camada
        fields = layer.fields()
        return fields
    
    def executePlugin(self, nome_camada, checkboxes, unir_bool, dissolve_bool, multipart_bool, merge_bool):
        
        # Abrir camada pelo nome
        camada = self.openLayer(nome_camada)
        
        # Verificar se a camada foi carregada corretamente
        if not camada.isValid():
            print("Não foi possível carregar a camada vetorial!")
        else:
            # Criar uma lista para armazenar os nomes dos campos marcados
            campos_marcados = []

            # Verificar quais checkboxes estão marcados
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    campos_marcados.append(checkbox.text())

            # Exibir os nomes dos campos marcados
            print("Campos marcados:", campos_marcados)

            # Obter todos os campos da camada
            campos = self.fieldsLayer(camada)

            # Dicionário para armazenar os valores únicos para cada campo
            valores_unicos_por_campo = {}

            # Loop sobre os campos
            for campo in campos_marcados:
                nome_campo = campo
                valores_unicos_por_campo[nome_campo] = set()
                # Loop sobre as features da camada para obter os valores únicos para cada campo
                for feature in camada.getFeatures():
                    valor = feature[nome_campo]
                    # Adicionar o valor ao conjunto de valores únicos para o campo atual
                    valores_unicos_por_campo[nome_campo].add(valor)

            # Mostrar os valores únicos para cada campo
            print("Valores únicos para cada campo:")
            campos_features = {}
            # campos_valores = {}
            for campo, valores_unicos in valores_unicos_por_campo.items():
                print(f"Campo: {campo}")
                # campos_valores.append(campo)
                for valor in valores_unicos:
                    print(valor)
                campos_features[campo] = valores_unicos
                print("---------------------")
    
            # Variável com todos os valores para 'densidade'
            # densidades = [
                # 'Densa','Pouco densa','Loteamento vazio'
            # ]
            # Variável com todos os valores para 'tipo'
            # tipos = [
                # 'Área Urbanizada','Outros equipamentos urbanos','Vazio intraurbano','Loteamento vazio'
            # ]
            # Variável com todos os valores para 'comparacao'
            # comparacoes = [
                # 'Adição','Densificação','Reclassificado','Sem alteração','Adição de loteamento vazio','Adição em loteamento vazio','Subtração de loteamento vazio','Subtração','Exclusão','Desdensificação','Não mapeado'
            # ]
            
            # for i in range(total_campos):
                # expressao = campos_valores[i]+" = '"+densidade+"' AND Tipo = '"+tipo+"' AND Comparacao = '"+comparacao+"'"

            # Lista para armazenar os valores únicos de cada campo
            valores_campos = {}

            # Iterar sobre os nomes dos campos para obter os valores únicos de cada campo
            for campo_valor in campos_marcados:
                valores_campos[campo_valor] = []

            # Obtém os valores únicos de cada campo
            for feature in camada.getFeatures():
                for campo in campos_marcados:
                    valor = feature[campo]
                    if valor not in valores_campos[campo]:
                        valores_campos[campo].append(valor)

            # Lista para armazenar as expressões
            expressoes = []

            # Gerar todas as combinações dos valores dos campos
            combinacoes = list(itertools.product(*(valores_campos[campo] for campo in campos_marcados)))

            # Gerar a expressão para cada combinação
            for combinacao in combinacoes:
                expressao = ''
                for i, campo in enumerate(campos_marcados):
                    expressao += f"{campo} = '{combinacao[i]}'"
                    if i < len(campos_marcados) - 1:
                        expressao += " AND "
                expressoes.append(expressao)

            # Mostrar as expressões geradas
            for i, exp in enumerate(expressoes, 1):
                print(f"expressao[{i}] = {exp}")
            
            count_times = 0
            total_loop = len(expressoes)
            caminhos_saidas_multipart = []
            total_campos = len(campos_features)
            
            for expressao in expressoes:
                # Contagem
                count_times = count_times + 1
                print(f"Contagem: {count_times} / {total_loop}")
                
                # Substituir espaços por underscores
                expressao_spaces = expressao.replace(' ', '_')
                # Substituir sinal de igual por underscore
                expressao_spaces_equal = expressao_spaces.replace('=', '')
                # Substituir sinal de igual por underscore
                expressao_spaces_equal_apostrophe = expressao_spaces_equal.replace("'", '')
                # Formatar o nome da camada com base no índice e no nome da camada
                nome_camada_multipart = f"Camada_{count_times}_{expressao_spaces_equal_apostrophe}_"
                #nome_camada_merge = f"Camada_{count_times}_{expressao_spaces_equal_apostrophe}_"
                
                # Expressão de seleção
                # expressao = "Densidade = '"+densidade+"' AND Tipo = '"+tipo+"' AND Comparacao = '"+comparacao+"'"
                print(f"Expressão: {expressao}")

                # Selecionar os polígonos que atendem à expressão
                camada.selectByExpression(expressao)

                # Obter somente as feições selecionadas
                feicoes_selecionadas = camada.selectedFeatures()

                if feicoes_selecionadas:
                    print(f"Número de polígonos selecionados: {len(feicoes_selecionadas)}")
                    print(f"Executando...")
                    
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
                    resultado_join = {}
                    if (unir_bool):
                        resultado_join = processing.run("qgis:joinbylocationsummary", {
                           'INPUT':QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True),
                           'PREDICATE':[3],
                           'JOIN':QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True),
                           'JOIN_FIELDS':[],
                           'SUMMARIES':[0],
                           'DISCARD_NONMATCHING':False,
                           'OUTPUT': 'TEMPORARY_OUTPUT'
                        })
                    else:
                        resultado_join['OUTPUT'] = QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True)
                    
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
                        resultado_dissolve = {}
                        if (dissolve_bool):
                            resultado_dissolve = processing.run("native:dissolve", {
                                'INPUT': caminho_temporario_saida,
                                'FIELD': [],  # Dissolver com base nos campos
                                'SEPARATE_DISJOINT': False,
                                'OUTPUT': 'TEMPORARY_OUTPUT'
                            })
                        else:
                            if (unir_bool):
                                resultado_dissolve['OUTPUT'] = resultado_join['OUTPUT']
                            else:
                                resultado_dissolve['OUTPUT'] = QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True)

                        if 'OUTPUT' in resultado_dissolve:
                            caminho_temporario_saida_dissolve = resultado_dissolve['OUTPUT']
                            
                            # caminho_saida_multipart = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/Poligonos/'+nome_camada_multipart
                            resultado_multipart = {}
                            if (multipart_bool):
                                resultado_multipart = processing.run("native:multiparttosingleparts", {
                                    'INPUT': caminho_temporario_saida_dissolve,
                                    'OUTPUT': 'TEMPORARY_OUTPUT'
                                })
                            else:
                                if (dissolve_bool):
                                    resultado_multipart['OUTPUT'] = resultado_dissolve['OUTPUT']
                                else:
                                    if (unir_bool):
                                        resultado_multipart['OUTPUT'] = resultado_join['OUTPUT']
                                    else:
                                        resultado_multipart['OUTPUT'] = QgsProcessingFeatureSourceDefinition(camada.source(), selectedFeaturesOnly=True)

                            if 'OUTPUT' in resultado_multipart:
                                
                                caminho_temporario_saida_multipart = resultado_multipart['OUTPUT']
                                
                                caminhos_saidas_multipart.append(caminho_temporario_saida_multipart)
                                
                                print(f"Nome da Camada: {nome_camada_multipart}")
                                # nova_camada = QgsVectorLayer(caminho_temporario_saida_multipart, nome_camada_multipart, "ogr")
                                
                                # Adicionar a camada temporária ao Map Layer
                                caminho_temporario_saida_multipart.setName(nome_camada_multipart)
                                QgsProject.instance().addMapLayer(caminho_temporario_saida_multipart)

                                # if not nova_camada.isValid():
                                    # print("Erro ao carregar a camada resultante.")
                                # else:
                                    # QgsProject.instance().addMapLayer(nova_camada)                                                
                                    # print("Processamento concluído com sucesso.")
                                # Obtenha a camada temporária usando o nome da saída
                                # camada_temporaria = QgsProcessingUtils.mapLayer(caminho_temporario_saida_multipart)
                                # if not camada_temporaria.isValid():
                                    # print("Erro ao carregar a camada resultante.")
                                # else:
                                    # camada_temporaria.setName(nome_camada_multipart)
                                    # QgsProject.instance().addMapLayer(camada_temporaria)                                                
                                    # print("Processamento concluído com sucesso.")
                            else:
                                print("Erro ao executar o algoritmo de dividir (multiparttosingleparts).")
                        else:
                            print("Erro ao executar o algoritmo de dissolver.")
                    else:
                        print("Erro ao executar o algoritmo de junção.")

                else:
                    print("Nenhum polígono selecionado.")
                    print(f"Executando próximo...")
            if (merge_bool):
                # Executar o algoritmo para mesclar as camadas
                nome_camada_merge = f"Camada_{nome_camada}_Merge_{count_times}_Layers"
                # caminho_saida_merge = 'C:/Users/j_sil/OneDrive/Documentos/Lizandra/QGis/Shapes/Poligonos/'+nome_camada_merge
                resultado_mescla = processing.run("native:mergevectorlayers", {
                    'LAYERS': caminhos_saidas_multipart,
                    'CRS': 'EPSG:4674',  # Defina o CRS desejado
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                })
                if 'OUTPUT' in resultado_dissolve:
                    caminho_temporario_saida_merge = resultado_mescla['OUTPUT']
                    caminho_temporario_saida_merge.setName(nome_camada_merge)
                    QgsProject.instance().addMapLayer(caminho_temporario_saida_merge)
                    # nova_camada_merge = QgsVectorLayer(caminho_temporario_saida_merge, nome_camada_multipart, "ogr")
                    # if not nova_camada_merge.isValid():
                        # print("Erro ao carregar a camada resultante.")
                    # else:
                        # QgsProject.instance().addMapLayer(nova_camada_merge)                                                
                        # print("Processamento concluído com sucesso.")
                    # camada_temporaria_merge = QgsProcessingUtils.mapLayer(resultado_dissolve['OUTPUT'])
                    # if not camada_temporaria_merge.isValid():
                        # print("Erro ao carregar a camada resultante.")
                    # else:
                        # camada_temporaria_merge.setName(nome_camada_merge)
                        # QgsProject.instance().addMapLayer(camada_temporaria_merge)                                                
                        # print("Processamento concluído com sucesso.")
                else:
                    print("Erro ao executar o algoritmo de mesclar.")
            print("Operação finalizada com sucesso.")

    
