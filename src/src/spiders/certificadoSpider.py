import scrapy


class certificadoSpider(scrapy.Spider):
    name = 'certificado'
    file_urls = []

    def __init__(self):
        self.opcao_campus = '13'
        self.opcao_todos_anos = ""        # O valor que representa todos é str vazia
        self.opcao_selecione_eventos = "" # O valor que representa o selecione é str vazia
        self.nome_aluno = 'EDUARDO RODRIGO DE OLIVEIRA'
        self.num_form_evento = 2
        self.base_link_download = 'http://apl.utfpr.edu.br/extensao/emitir/'

    def start_requests(self):
        urls = ['http://apl.utfpr.edu.br/extensao/listaPublica']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.set_campus)

    def set_campus(self, response):
        yield scrapy.http.FormRequest.from_response(
            response=response,
            formdata={'txtCampus': self.opcao_campus,
                      'txtAno': self.opcao_todos_anos,
                      'txtEvento': self.opcao_selecione_eventos},
            callback=self.request_eventos
        )

    def request_eventos(self, response):
        eventos = response.css('div.form_left select')[self.num_form_evento]
        eventos = eventos.css('option::attr(value)').getall()
        for evento in eventos[1:]:
            yield scrapy.http.FormRequest.from_response(
            response=response,
            formdata={'txtCampus': self.opcao_campus,
                      'txtAno': self.opcao_todos_anos,
                      'txtEvento': evento},
            callback=self.busca_nome
        )

    def busca_nome(self, response):
        yield scrapy.http.FormRequest.from_response(
            response=response,
            formdata={
                'cmdPesquisa':'D', # D é pessoa
                'txtPesquisa':self.nome_aluno
            },
            callback=self.busca_certificado
        )

    def busca_certificado(self, response):
        linhasTabelaPessoas = response.css('table tr')
        for linha in linhasTabelaPessoas:
            link_detalhes = linha.css('td a::attr(href)').get()
            if link_detalhes != None:
                codigo_download = link_detalhes.split('/')[-1]
                link_download = self.base_link_download + codigo_download
                print(link_download)
                yield {'file_urls':[link_download]}
