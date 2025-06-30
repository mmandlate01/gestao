from wsgiref.simple_server import make_server
from urllib.parse import parse_qs

requests = []

def render_index():
    return f"""<html><body>
<h1>Assist\u00eancia</h1>
<p>Total de pedidos: {len(requests)}</p>
<p><a href='/requests/new'>Novo Pedido</a></p>
<p><a href='/requests'>Ver Pedidos</a></p>
</body></html>"""


def render_new():
    return """<html><body>
<h1>Novo Pedido de Assist\u00eancia</h1>
<form method='post' action='/requests'>
Nome:<br><input name='name'><br>
Contato:<br><input name='contact'><br>
Problema:<br><textarea name='issue'></textarea><br>
<button type='submit'>Enviar</button>
</form>
<p><a href='/'>Voltar</a></p>
</body></html>"""


def render_list():
    rows = ""
    for r in requests:
        rows += f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['contact']}</td><td>{r['issue']}</td><td>{r['status']}</td><td>{r.get('attendedBy', '')}</td>"
        if r['status'] == 'pendente':
            rows += f"<td><form method='post' action='/requests/{r['id']}/attend'><input name='attendedBy'><button type='submit'>Atender</button></form></td>"
        else:
            rows += "<td></td>"
        rows += "</tr>"
    return f"""<html><body>
<h1>Pedidos de Assist\u00eancia</h1>
<table border='1'><tr><th>ID</th><th>Nome</th><th>Contato</th><th>Problema</th><th>Status</th><th>Atendido Por</th><th>A\u00e7\u00f5es</th></tr>{rows}</table>
<p><a href='/'>Voltar</a></p>
</body></html>"""


def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    if method == 'GET' and path == '/':
        data = render_index().encode()
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', str(len(data)))])
        return [data]
    if method == 'GET' and path == '/requests':
        data = render_list().encode()
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', str(len(data)))])
        return [data]
    if method == 'GET' and path == '/requests/new':
        data = render_new().encode()
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', str(len(data)))])
        return [data]
    if method == 'POST' and path == '/requests':
        size = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(size).decode()
        params = parse_qs(body)
        name = params.get('name', [''])[0]
        contact = params.get('contact', [''])[0]
        issue = params.get('issue', [''])[0]
        rid = len(requests) + 1
        requests.append({'id': rid, 'name': name, 'contact': contact, 'issue': issue, 'status': 'pendente'})
        start_response('303 See Other', [('Location', '/requests')])
        return [b'']
    if method == 'POST' and path.startswith('/requests/') and path.endswith('/attend'):
        rid_str = path.split('/')[2]
        try:
            rid = int(rid_str)
        except ValueError:
            start_response('400 Bad Request', [('Content-Type', 'text/plain')])
            return [b'Invalid ID']
        size = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(size).decode()
        params = parse_qs(body)
        attended_by = params.get('attendedBy', [''])[0]
        for r in requests:
            if r['id'] == rid:
                r['status'] = 'atendido'
                r['attendedBy'] = attended_by
                break
        start_response('303 See Other', [('Location', '/requests')])
        return [b'']
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']


if __name__ == '__main__':
    with make_server('', 8000, app) as server:
        print('Servidor executando em http://localhost:8000/')
        server.serve_forever()
