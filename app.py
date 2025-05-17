import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class Agent:
    def __init__(self, name, model, instruction, description, tools=None):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.description = description
        self.tools = tools if tools is not None else []

    def run(self, input_prompt):
        prompt_with_instruction = f"{self.instruction}\\n\\n{input_prompt}"
        response = self.model.generate_content(prompt_with_instruction)
        return response.text

def call_agent(agent, input_prompt):
    return agent.run(input_prompt)

# --- Agente 1: Buscador de Informações Gerais ---
def agente_buscador(localizacao, preferencias_rotas):
    buscador = Agent(
        name="agente_buscador_geral",
        model=model,
        instruction=f"""
        Você é um assistente de pesquisa especializado em encontrar informações relevantes sobre diversas categorias em uma dada localização.
        Sua tarefa é utilizar o Google Search para encontrar informações sobre:
        - Trilhas, parques, áreas verdes e ruas tranquilas adequadas para caminhada e corrida na localização fornecida: {localizacao}, considerando as preferências: {preferencias_rotas}.
        - Bares e restaurantes mais bem avaliados no Google Maps na localização: {localizacao}. Priorize aqueles com boas avaliações (4.0 estrelas ou mais) e um bom número de avaliações.
        - Pontos turísticos mais bem avaliados no Google Maps na localização: {localizacao}. Priorize aqueles com boas avaliações e descrições interessantes.

        Para cada categoria, forneça uma lista concisa de até 3 sugestões, incluindo o nome e uma breve descrição ou detalhes relevantes encontrados na busca.
        """,
        description="Agente que busca informações sobre rotas, bares, restaurantes e pontos turísticos.",
    )
    entrada_do_agente_buscador = f"Localização: {localizacao}\\nPreferências de Rotas: {preferencias_rotas}"
    return call_agent(buscador, entrada_do_agente_buscador)

# --- Agente 2: Planejador de Experiências ---
def agente_planejador(localizacao, preferencias_rotas, resultados_busca):
    planejador = Agent(
        name="agente_planejador_experiencias",
        model=model,
        instruction=f"""
        Você é um planejador de experiências especializado em organizar informações sobre rotas, bares, restaurantes e pontos turísticos.
        Com base nos resultados da busca ({resultados_busca}) para a localização ({localizacao}) e nas preferências de rotas ({preferencias_rotas}), sua tarefa é:
        - Organizar as informações encontradas em categorias claras: Rotas, Bares, Restaurantes e Pontos Turísticos.
        - Para cada categoria, liste as sugestões com o nome e a descrição fornecida pelo agente buscador.
        """,
        description="Agente que organiza as informações para o usuário.",
    )
    entrada_do_agente_planejador = f"Localização: {localizacao}\\nPreferências de Rotas: {preferencias_rotas}\\nResultados da Busca: {resultados_busca}"
    return call_agent(planejador, entrada_do_agente_planejador)

# --- Agente 3: Detalhador de Opções ---
def agente_detalhador(localizacao, plano_experiencias):
    detalhador = Agent(
        name="agente_detalhador_opcoes",
        model=model,
        instruction=f"""
        Você é um especialista em fornecer detalhes adicionais sobre as opções de rotas, bares, restaurantes e pontos turísticos em {localizacao}.
        Com base no plano de experiências ({plano_experiencias}), escolha uma opção de cada categoria e busque mais detalhes relevantes sobre ela no Google Search.
        Para rotas, procure informações sobre o percurso, dificuldade e pontos de interesse.
        Para bares e restaurantes, procure informações sobre o tipo de ambiente, especialidades e avaliações.
        Para pontos turísticos, procure informações sobre o que torna o local interessante e o que os visitantes podem esperar.
        Apresente esses detalhes de forma concisa.
        """,
        description="Agente que fornece detalhes sobre as opções.",
    )
    entrada_do_agente_detalhador = f"Localização: {localizacao}\\nPlano de Experiências: {plano_experiencias}"
    return call_agent(detalhador, entrada_do_agente_detalhador)

# --- Agente 4: Avaliador e Recomendador ---
def agente_avaliador(localizacao, preferencias_rotas, detalhes_opcoes):
    avaliador = Agent(
        name="agente_avaliador_recomendador",
        model=model,
        instruction=f"""
        Você é um avaliador e recomendador de experiências em {localizacao}.
        Com base nos detalhes das opções ({detalhes_opcoes}) e nas preferências de rotas do usuário ({preferencias_rotas}), forneça algumas recomendações personalizadas.
        Destaque as opções que melhor se encaixam nas preferências do usuário e explique o porquê.
        Ofereça sugestões de como combinar diferentes atividades (ex: uma caminhada seguida de um almoço em um restaurante bem avaliado).
        """,
        description="Agente que avalia as opções e faz recomendações.",
    )
    entrada_do_agente_avaliador = f"Localização: {localizacao}\\nPreferências de Rotas: {preferencias_rotas}\\nDetalhes das Opções: {detalhes_opcoes}"
    return call_agent(avaliador, entrada_do_agente_avaliador)

def main():
    st.title("📍 ExplorAI: Rotas, Sabores e Tesouros Locais 🗺️")

    localizacao = st.text_input("Digite a sua LOCALIZAÇÃO:", "São Sebastião, SP")
    preferencias_rotas = st.text_area("Quais são suas PREFERÊNCIAS para a rota? (ex: distância, nível de dificuldade, tipo de paisagem):", "Distância: 5-10 km, Nível: Moderado, Paisagem: Praia e trilha")

    if st.button("Explorar Local"):
        if not localizacao:
            st.error("Por favor, digite sua localização.")
        else:
            st.info(f"Buscando informações para: {localizacao}...")

            with st.spinner("Buscando informações gerais..."):
                resultados_busca = agente_buscador(localizacao, preferencias_rotas)
                st.subheader("🔍 Resultados da Busca:")
                st.markdown(resultados_busca)

            with st.spinner("Organizando as opções..."):
                plano_experiencias = agente_planejador(localizacao, preferencias_rotas, resultados_busca)
                st.subheader("🗺️ Plano de Experiências:")
                st.markdown(plano_experiencias)

            with st.spinner("Detalhando as opções..."):
                detalhes_opcoes = agente_detalhador(localizacao, plano_experiencias)
                st.subheader("✨ Detalhes das Opções:")
                st.markdown(detalhes_opcoes)

            with st.spinner("Gerando recomendações personalizadas..."):
                recomendacoes_finais = agente_avaliador(localizacao, preferencias_rotas, detalhes_opcoes)
                st.subheader("💡 Recomendações Personalizadas:")
                st.markdown(recomendacoes_finais)

if __name__ == "__main__":
    main()