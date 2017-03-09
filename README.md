#Fixed Width Text

Biblioteca Python baseado no model do django para ler e escrever arquivos com tamanho de linha fixo.

##instalação
pip install fixedwidthtext


##Exemplo
###Criando classe para ler/escrever
```python
import datetime

from fixedwidthtext.models import LineManager
from fixedwidthtext import fields

class Header(LineManager):
    sequencial = fields.IntegerField(size=6, verbose_name='Número seqüencial')
    nome = fields.CharField(max_length=30)
    nascimento = fields.DateField(default=datetime.datetime.now)
    salario = fields.DecimalField(size=8, decimal_places=2)

```
###Lendo linha
```python
linha = '000001Joao Ferreira                 1999100100020000'
teste = Header(string=linha)
teste.get_dicts()
[
  {
    'name': 'sequencial',
    'value': 1,
    'verbose_name': 'N\xc3\xbamero seq\xc3\xbcencial'},
  {
    'name': 'nome',
    'value': 'Joao Ferreira',
    'verbose_name': 'nome'},
  {
    'name': 'nascimento',
    'value': datetime.date(1999, 10, 1),
    'verbose_name': 'nascimento'},
  {
    'name': 'salario',
    'value': Decimal('200.00'),
    'verbose_name': 'salario'}
]

# Ou acessando direto
teste.sequencial
1

teste.nome
'Joao Ferreira'

teste.salario
Decimal('200.00')

teste.nascimento
datetime.date(1999, 10, 1)
```

###Escrevendo linha
```python
import datetime
from decimal import Decimal

teste = Header(nome='Maria serena', nascimento=datetime.date(2000, 10, 2), salario=Decimal(3000), sequencial=2)
teste.to_string()
'000002Maria serena                  2000100200300000'
```

