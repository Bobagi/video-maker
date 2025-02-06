import os
import unicodedata

class RoteiroProcessor:
    def __init__(self, input_path):
        self.input_path = input_path
        self.roteiros = []
        
    def processar(self):
        """Método principal para executar todo o processamento"""
        conteudo = self._ler_arquivo()
        self.roteiros = self._dividir_roteiros(conteudo)
        
    def exportar(self, output_dir='scripts'):
        """
        Exporta os roteiros para arquivos individuais
        :param output_dir: Diretório de saída (padrão: scripts)
        """
        os.makedirs(output_dir, exist_ok=True)
        for roteiro in self.roteiros:
            nome_arquivo = self._gerar_nome_arquivo(roteiro)
            caminho_completo = os.path.join(output_dir, nome_arquivo)
            with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
                print(f"Roteiro criado: {caminho_completo}")
                arquivo.write(roteiro)
                
    def _ler_arquivo(self):
        """Lê o conteúdo do arquivo de entrada"""
        with open(self.input_path, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
            
    def _dividir_roteiros(self, conteudo):
        """Divide o conteúdo em roteiros individuais baseado em 'TEMA:'"""
        roteiros = []
        bloco_atual = []
        
        for linha in conteudo.split('\n'):
            if linha.startswith('TEMA: '):
                if bloco_atual:  # Se já temos um bloco em andamento
                    roteiros.append('\n'.join(bloco_atual))
                    bloco_atual = []
                bloco_atual.append(linha)
            else:
                if bloco_atual:  # Só adiciona se já tivermos um TEMA
                    bloco_atual.append(linha)
        
        # Adiciona o último bloco
        if bloco_atual:
            roteiros.append('\n'.join(bloco_atual))
            
        return roteiros
    
    def _gerar_nome_arquivo(self, conteudo_roteiro):
        """Gera o nome do arquivo baseado no tema do roteiro"""
        for linha in conteudo_roteiro.split('\n'):
            if linha.startswith('TEMA: '):
                tema = linha.split(': ', 1)[1].split(':')[0].strip()
                break
        
        nome_base = self._normalizar_nome(tema)
        return f"{nome_base}.txt"
    
    def _normalizar_nome(self, texto):
        """Normaliza o texto para criar nomes de arquivo válidos"""
        texto_sem_acentos = self._remover_acentos(texto)
        palavras = texto_sem_acentos.split()
        return ''.join(palavra.capitalize() for palavra in palavras)
    
    @staticmethod
    def _remover_acentos(texto):
        """Remove acentos e caracteres especiais"""
        texto_normalizado = unicodedata.normalize('NFKD', texto)
        return ''.join(c for c in texto_normalizado if not unicodedata.combining(c))

    def deletar_arquivo_original(self):
        """Remove o arquivo fonte original após o processamento"""
        if os.path.exists(self.input_path):
            try:
                os.remove(self.input_path)
                print(f"Arquivo original {self.input_path} removido com sucesso!")
            except OSError as e:
                print(f"Erro ao deletar arquivo: {e.strerror}")
        else:
            print(f"Arquivo {self.input_path} não encontrado para remoção")

# Exemplo de uso
if __name__ == "__main__":
    processor = RoteiroProcessor(os.path.join("scripts", "roteiro.txt"))
    processor.processar()
    processor.exportar("scripts")
    processor.deletar_arquivo_original()
    
    print(f"Foram criados {len(processor.roteiros)} arquivos com sucesso!")