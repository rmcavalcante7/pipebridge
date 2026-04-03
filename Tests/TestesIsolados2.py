import requests

url = 'https://app.pipefy.com/queries'
auth_key="eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NzUwNDM0NDcsImp0aSI6ImFhZjQ0N2UyLWI1NzQtNGE3NS1hMzYxLTc3ZWM4NWYwNjA1ZiIsInN1YiI6MzA1Njc0MzA1LCJ1c2VyIjp7ImlkIjozMDU2NzQzMDUsImVtYWlsIjoicmFmYWVsLm0uY2F2YWxjYW50ZUBhY2NlbnR1cmUuY29tIn0sInVzZXJfdHlwZSI6ImF1dGhlbnRpY2F0ZWQifQ.wS973IfL2-Y3EaO4KnEt4oyz8yrLpCNjlRfoFvt2JhrcNmXSGOq_WAfgM1jAjbJCUmHpDNWbRlDJd2szDvbgmw"

# Substitua pelo seu token pessoal
headers = {
    "Authorization": f"Bearer {auth_key}",
    "Content-Type": "application/json"
}

# Dados que você forneceu (Payload)
# Mutation oficial para atualizar qualquer campo de card
payload = {
    "query": """
    mutation {
      updateCardField(input: {
        card_id: "1328390184",
        field_id: "aprovado",
        new_value: "Sim"
      }) {
        success
        card {
          id
        }
      }
    }
    """
}



response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Atualização concluída!")
    print(response.json())
else:
    print(f"Erro {response.status_code}: {response.text}")