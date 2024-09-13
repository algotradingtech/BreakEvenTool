import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Configuration de la page Streamlit
st.set_page_config(
    page_title="TradingAlgotech Tool #1",  # Titre de la page
    page_icon="💹",  # Icône (favicon)
    layout="centered",   # "centered" ou "wide"
    initial_sidebar_state="expanded"  # État de la barre latérale ("collapsed" ou "expanded")
)
st.header("📲 👉 🔄 📱")
st.title("Tableau et Graphique : Break even et Gain Moyen par Trade")

# Section 1: Création du tableau avec formatage en pourcentages
st.header("Tableau de Breakeven par Risk-Reward Ratio et Taux de Réussite")

# Création du tableau avec le Risk-Reward Ratio jusqu'à 10
risk_reward_ratios = np.arange(1, 11, 1)  # De 1 à 10
win_rates = np.arange(0, 101, 10)  # De 0 à 100% avec un pas de 10%

# Fonction pour calculer l'espérance de profit
def calculate_expected_profit_matrix(risk_reward_ratio, win_rate):
    win_rate_fraction = win_rate / 100
    expected_profit = (win_rate_fraction * risk_reward_ratio) - ((1 - win_rate_fraction) * 1)
    return expected_profit*100 # Ne pas multiplier par 100 ici, on garde les valeurs brutes

# Génération du tableau
data = []
for rrr in risk_reward_ratios:
    row = [calculate_expected_profit_matrix(rrr, wr) for wr in win_rates]
    data.append(row)

# Création du DataFrame et conversion en pourcentages
df = pd.DataFrame(data, index=[f"RRR {r}" for r in risk_reward_ratios], columns=[f"{wr}%" for wr in win_rates])

# Mise en forme conditionnelle avec des couleurs et un formatage en pourcentages
styled_df = df.style.format("{:.2f}%").applymap(lambda v: 'background-color: yellow' if v == 0 else
                                               'background-color: red' if v < 0 else
                                               'background-color: green' if v > 0 else '')

# Affichage du tableau avec mise en forme conditionnelle
st.dataframe(styled_df)

# Explication du tableau
st.markdown("""
### Interprétation du tableau :
- **Vert** : Espérance de profit positive (stratégie rentable).
- **Jaune** : Breakeven, ni perte ni gain (0%).
- **Rouge** : Espérance de profit négative (stratégie perdante).
""")

# Section 2 : Calcul du breakeven et graphique interactif

st.header("Calculateur de Breakeven et Gain Moyen par Trade")

# Entrée utilisateur pour le Risk-Reward Ratio via un slider
risk_reward_ratio = st.slider("Sélectionnez votre Risk-Reward Ratio **(Ex: 1:2 = 2)**", min_value=0.5, max_value=10.0, step=0.1, value=2.0)

# Choix de l'unité des frais : pourcentage ou pips
fee_option = st.radio("Sélectionnez l'unité des frais :", ('Pourcentage (%)', 'Pips'))

if fee_option == 'Pourcentage (%)':
    broker_fees = st.number_input("Entrez les frais du broker en %", min_value=0.0, value=0.0)
else:
    pips = st.number_input("Entrez les frais du broker en pips", min_value=0.0, value=0.0)
    broker_fees = pips * 0.01
    st.write(f"Les frais en pourcentage sont : **{broker_fees:.2f}%**")

# Fonction pour calculer le breakeven
def calculate_breakeven(risk_reward_ratio, broker_fees):
    breakeven_win_rate = 1 / (1 + risk_reward_ratio)
    breakeven_win_rate += broker_fees / 100  # Intégration des frais du broker
    return breakeven_win_rate * 100  # On convertit ici en pourcentage

# Calcul du breakeven en pourcentage
breakeven = calculate_breakeven(risk_reward_ratio, broker_fees)

# Affichage du taux de réussite nécessaire pour être à breakeven
st.write(f"Pour être à breakeven avec un Risk-Reward Ratio de **{risk_reward_ratio}**:1 et des frais de **{broker_fees:.2f}%**, vous devez réussir au moins **{breakeven:.2f}%** de vos trades.")

# Générer des taux de réussite de 0 à 100%
win_rates = np.linspace(0, 100, 100)

# Fonction pour calculer le gain moyen en fonction du taux de réussite
def calculate_expected_profit(win_rate, risk_reward_ratio, broker_fees):
    win_rate_fraction = win_rate / 100
    expected_profit = (win_rate_fraction * risk_reward_ratio) - ((1 - win_rate_fraction) * 1)
    expected_profit_after_fees = expected_profit - (broker_fees / 100)
    return expected_profit_after_fees * 100# Multiplier ici pour afficher les résultats en %

# Calcul des profits pour chaque taux de réussite
expected_profits = [calculate_expected_profit(wr, risk_reward_ratio, broker_fees) for wr in win_rates]

# Création du graphique Plotly pour visualiser le gain moyen et le breakeven
fig = go.Figure()

# Courbe du gain moyen (bien ajustée en pourcentage)
fig.add_trace(go.Scatter(x=win_rates, y=expected_profits, mode='lines', name='Gain Moyen', line=dict(color='green')))

# Courbe du breakeven (toujours à 0% pour indiquer le seuil de rentabilité)
fig.add_trace(go.Scatter(x=win_rates, y=[0]*100, mode='lines', name='Breakeven', line=dict(color='red', dash='dash')))

# Ajout d'une ligne horizontale pour aider la lecture du graphique
fig.update_layout(
    shapes=[dict(
        type='line',
        y0=0, y1=0, x0=0, x1=100,
        line=dict(color='red', dash='dash'),
    )]
)

# Configuration du graphique avec tickformat basé sur une échelle de 100 (pour les pourcentages)
fig.update_layout(
    title="Gain Moyen (%) par Trade en fonction du Taux de Réussite",
    xaxis_title="Taux de Réussite (%)",
    yaxis_title="Gain Moyen (%) de la somme risquée",
    xaxis=dict(range=[0, 100], tickformat=".0f",ticksuffix=" %"),
    yaxis=dict(range=[-100, 200], tickformat=".0f",ticksuffix=" %"),
    template="plotly_dark"
)

st.plotly_chart(fig)

# Section explicative pour le graphique
st.markdown("""
### Interprétation du graphique :
- **Gain moyen** : Le pourcentage de la somme risquée que vous gagnez ou perdez en moyenne sur chaque trade.
- La ligne **rouge** représente le **breakeven**, où vous ne gagnez ni ne perdez à long terme.
- Le point où la courbe verte croise la ligne rouge indique le **taux de réussite minimum** nécessaire pour être rentable.
""")

### Section 3 : Gain ou perte en euros après plusieurs trades

st.header("Calculateur de Gain ou Perte en Euros après plusieurs Trades")

# Entrée de l'utilisateur : somme risquée par trade en euros
risk_per_trade = st.number_input("Entrez la somme risquée par trade (€)", min_value=1.0, value=100.0,step = 1.0)

# Entrée de l'utilisateur : nombre de trades via un slider
num_trades = st.slider("Nombre de trades effectués", min_value=1, max_value=1000, step=1, value=100)

# Fonction pour calculer le gain total ou la perte en euros
def calculate_total_gain_in_euros(win_rate, risk_reward_ratio, broker_fees, risk_per_trade, num_trades):
    win_rate_fraction = win_rate / 100
    # Gain moyen par trade (en pourcentage)
    expected_profit = (win_rate_fraction * risk_reward_ratio) - ((1 - win_rate_fraction) * 1)
    expected_profit_after_fees = expected_profit - (broker_fees / 100)
    # Gain total en euros après tous les trades
    total_gain = expected_profit_after_fees * risk_per_trade * num_trades
    return total_gain

# Calcul du gain en euros pour chaque taux de réussite
total_gains_euros = [calculate_total_gain_in_euros(wr, risk_reward_ratio, broker_fees, risk_per_trade, num_trades) for wr in win_rates]

# Création du graphique Plotly pour visualiser le gain total ou la perte en euros
fig_euros = go.Figure()

# Courbe du gain ou de la perte en euros
fig_euros.add_trace(go.Scatter(x=win_rates, y=total_gains_euros, mode='lines', name='Gain/Perte (€)', line=dict(color='blue')))

# Courbe du breake
# Courbe du breakeven en euros (c'est toujours 0, car à breakeven on ne gagne ni ne perd)
fig_euros.add_trace(go.Scatter(x=win_rates, y=[0]*100, mode='lines', name='Breakeven (€)', line=dict(color='red', dash='dash')))

# Configuration du graphique avec tickformat pour l'axe X en pourcentage et Y en euros
fig_euros.update_layout(
    title="Gain ou Perte Total(e) (€) après tous les Trades",
    xaxis_title="Taux de Réussite (%)",
    yaxis_title="Gain/Perte (€)",
    xaxis=dict(range=[0, 100], tickformat=".0f",ticksuffix=" %"),  # Affichage du taux de réussite sans décimales
    yaxis=dict(tickformat=",.0f",  # Affichage en euros, avec des espaces entre les milliers et sans centimes
               tickprefix="€"),    # Ajouter le symbole euro (€) devant les valeurs
    template="plotly_dark"
)


st.plotly_chart(fig_euros)

# Explication du graphique
st.markdown("""
### Interprétation du graphique :
- Ce graphique montre le **gain ou la perte total(e) en euros** après avoir effectué tous vos trades.
- La somme risquée par trade est celle que vous avez renseignée, et le nombre de trades est ajusté avec le slider.
- La ligne **rouge** représente le **breakeven**, où vous ne gagnez ni ne perdez à long terme.
- La courbe **bleue** montre si vous êtes en gain ou en perte total(e) en fonction de votre taux de réussite.
""")
