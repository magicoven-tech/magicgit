from http.server import HTTPServer, SimpleHTTPRequestHandler
import re
import os

class SSIHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Se for um arquivo HTML, processa os includes
        if self.path.endswith('.html') or self.path == '/':
            # Se for a raiz, serve o index.html
            if self.path == '/':
                self.path = '/index.html'
            
            try:
                # Abre o arquivo
                f = self.send_head()
                if f:
                    content = f.read().decode('utf-8')
                    
                    # Processa os includes
                    content = re.sub(
                        r'<!--#include\s+virtual=["\']([^"\']+)["\']\s*-->',
                        self._handle_include,
                        content
                    )
                    
                    # Envia o conteúdo processado
                    self.wfile.write(content.encode('utf-8'))
                    f.close()
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Para outros tipos de arquivo, usa o comportamento padrão
            return SimpleHTTPRequestHandler.do_GET(self)
    
    def _handle_include(self, match):
        """Processa um único include SSI"""
        include_path = match.group(1)
        try:
            # Tenta abrir o arquivo incluído
            with open(os.path.join(os.getcwd(), include_path.lstrip('/')), 'r') as f:
                return f.read()
        except Exception as e:
            return f"<!-- Erro ao incluir {include_path}: {str(e)} -->"

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SSIHTTPRequestHandler)
    print('Servidor rodando em http://localhost:8000')
    httpd.serve_forever()
