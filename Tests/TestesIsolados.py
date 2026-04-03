

from pipefy.client.httpClient import PipefyHttpClient


client = PipefyHttpClient(
    # auth_key="eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NzUwNDM0NDcsImp0aSI6ImFhZjQ0N2UyLWI1NzQtNGE3NS1hMzYxLTc3ZWM4NWYwNjA1ZiIsInN1YiI6MzA1Njc0MzA1LCJ1c2VyIjp7ImlkIjozMDU2NzQzMDUsImVtYWlsIjoicmFmYWVsLm0uY2F2YWxjYW50ZUBhY2NlbnR1cmUuY29tIn0sInVzZXJfdHlwZSI6ImF1dGhlbnRpY2F0ZWQifQ.wS973IfL2-Y3EaO4KnEt4oyz8yrLpCNjlRfoFvt2JhrcNmXSGOq_WAfgM1jAjbJCUmHpDNWbRlDJd2szDvbgmw",
    auth_key="eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NzUwNDM0NDcsImp0aSI6ImFhZjQ0N2UyLWI1NzQtNGE3NS1hMzYxLTc3ZWM4NWYwNjA1ZiIsInN1YiI6MzA1Njc0MzA1LCJ1c2VyIjp7ImlkIjozMDU2NzQzMDUsImVtYWlsIjoicmFmYWVsLm0uY2F2YWxjYW50ZUBhY2NlbnR1cmUuY29tIn0sInVzZXJfdHlwZSI6ImF1dGhlbnRpY2F0ZWQifQ.wS973IfL2-Y3EaO4KnEt4oyz8yrLpCNjlRfoFvt2JhrcNmXSGOq_WAfgM1jAjbJCUmHpDNWbRlDJd2szDvbgmw",
    base_url='https://app.pipefy.com/queries'

)

mutation = """
mutation {
  updateCardSelectFieldValue (
    input: {
      cardId: "1328390184"
      fieldId: "6e4331bb-74f5-4eca-b6d4-054a9e30bb6b" 
      value: "Sim"
    }
  ) {
    field {
      id
    }
  }
}
"""

# mutation = """
#     query {
#     phase(id: "342616255") {
#         id
#         name
#
#         fields {
#             id
#             label
#             type
#             required
#             description
#             options
#             uuid
#         }
#     }
# }
# """

# "descreva_o_motivo"
response = client.sendRequest(mutation)

print(response)