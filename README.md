# 🏆 TeamSeries - Sistema de Gerenciamento de Competições

Bem-vindo ao **TeamSeries**, um aplicativo em Python para gerenciamento de eventos esportivos por equipes, com pontuação customizável e classificação por categorias.

---

## 📋 Sobre o Projeto

O TeamSeries foi desenvolvido para facilitar a organização de competições esportivas em formato de equipes, permitindo:

- Cadastro de eventos com sistema de pontuação personalizado
- Cadastro de equipes por categoria (RX/SC)
- Cadastro de provas vinculadas ao evento
- Registro e edição de pontuação por prova e equipe
- Visualização do ranking final por categoria

---

## 🚀 Funcionalidades

- **Menu interativo no terminal**
- **Persistência de dados** via banco SQLite
- **Cadastro de eventos** com nome, sistema de pontuação e número de provas
- **Cadastro de equipes** (nome e categoria RX/SC)
- **Cadastro de provas** vinculadas ao evento
- **Registro de pontuação** por prova e equipe, com cálculo automático conforme sistema definido
- **Visualização de resultados** por categoria, exibindo ranking das equipes

---

## 🛠️ Como Usar

1. **Clone o repositório** e instale o Python 3.x.
2. Execute o aplicativo via terminal:

   ```bash
   python main.py
   ```

3. Siga as opções do menu para cadastrar eventos, equipes, provas, registrar pontuação e visualizar resultados.

---

## 🗂️ Estrutura do Projeto

```
TeamSeries/
├── main.py      # Lógica principal e menus
├── db.py        # Funções de banco de dados (SQLite)
```

---

## 💡 Exemplos de Uso

- **Cadastrar Evento:** Informe nome, sistema de pontuação (ex: `1:100,2:95,3:90,4:85,5:80`) e número de provas.
- **Cadastrar Equipes:** Informe nome e categoria (RX ou SC).
- **Cadastrar Provas:** Informe o nome de cada prova.
- **Adicionar Pontuação:** Selecione a prova e informe a colocação de cada equipe.
- **Visualizar Resultados:** Veja o ranking final por categoria.

---

## 📝 Observações

- O sistema exige pelo menos uma equipe por evento.
- Caso não haja eventos cadastrados, o menu orienta o usuário a criar um novo evento.
- Todos os dados são salvos automaticamente no banco de dados local (`teamseries.db`).

---

## 🤝 Contribuição

Sugestões, melhorias e correções são bem-vindas!  
Abra uma issue ou envie um pull request.

---

## 📄 Licença

Este projeto está sob a licença MIT.

---
