# feeding.py
# Calculadora de alimentação para psitacídeos
# Baseado em: NRC (National Research Council), Harrison & Lightfoot
# "Clinical Avian Medicine", e literatura especializada em avicultura

import math

# -------------------------------------------------------------------
# BASE DE DADOS NUTRICIONAIS POR ESPÉCIE
# TMB (Taxa Metabólica Basal) calculada pela fórmula alométrica:
# TMB (kcal/dia) = K * Peso(kg)^0.75
# K = 78 para não-passeriformes (psitacídeos) — fonte: Kleiber, NRC
# -------------------------------------------------------------------

ESPECIES_DADOS = {
    "periquito_australiano": {
        "nome": {"pt": "Periquito Australiano", "en": "Budgerigar", "fr": "Perruche Ondulée", "de": "Wellensittich"},
        "peso_medio_g": 35,
        "peso_min_g": 25,
        "peso_max_g": 45,
        "k_metabolico": 78,
        "proteina_manut_pct": 12,
        "gordura_manut_pct": 4,
        "fibra_max_pct": 6,
        "calcio_mg_kg": 4000,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 8000,
        "notas": {
            "pt": "Granívoro. Base: sementes pequenas + pellets + vegetais folhosos.",
            "en": "Granivore. Base: small seeds + pellets + leafy vegetables.",
            "fr": "Granivore. Base: petites graines + granulés + légumes feuillus.",
            "de": "Körnerfresser. Basis: kleine Samen + Pellets + Blattgemüse."
        }
    },
    "calopsita": {
        "nome": {"pt": "Calopsita", "en": "Cockatiel", "fr": "Calopsitte", "de": "Nymphensittich"},
        "peso_medio_g": 90,
        "peso_min_g": 70,
        "peso_max_g": 120,
        "k_metabolico": 78,
        "proteina_manut_pct": 12,
        "gordura_manut_pct": 4,
        "fibra_max_pct": 7,
        "calcio_mg_kg": 4000,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 8000,
        "notas": {
            "pt": "Granívoro. Base: sementes médias + pellets + vegetais + frutas com moderação.",
            "en": "Granivore. Base: medium seeds + pellets + vegetables + fruit in moderation.",
            "fr": "Granivore. Base: graines moyennes + granulés + légumes + fruits avec modération.",
            "de": "Körnerfresser. Basis: mittlere Samen + Pellets + Gemüse + Obst in Maßen."
        }
    },
    "agapornis": {
        "nome": {"pt": "Agapornis (Inseparável)", "en": "Lovebird", "fr": "Inséparable", "de": "Unzertrennlicher"},
        "peso_medio_g": 55,
        "peso_min_g": 40,
        "peso_max_g": 70,
        "k_metabolico": 78,
        "proteina_manut_pct": 13,
        "gordura_manut_pct": 5,
        "fibra_max_pct": 7,
        "calcio_mg_kg": 4500,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Granívoro/frugívoro. Base: sementes + pellets + frutas + vegetais verdes.",
            "en": "Granivore/frugivore. Base: seeds + pellets + fruits + green vegetables.",
            "fr": "Granivore/frugivore. Base: graines + granulés + fruits + légumes verts.",
            "de": "Körnerfresser/Frugivore. Basis: Samen + Pellets + Früchte + grünes Gemüse."
        }
    },
    "pyrrhura": {
        "nome": {"pt": "Pyrrhura (Tiriba)", "en": "Pyrrhura Conure", "fr": "Conure Pyrrhura", "de": "Pyrrhura Sittich"},
        "peso_medio_g": 75,
        "peso_min_g": 55,
        "peso_max_g": 95,
        "k_metabolico": 78,
        "proteina_manut_pct": 14,
        "gordura_manut_pct": 5,
        "fibra_max_pct": 8,
        "calcio_mg_kg": 4500,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Frugívoro/granívoro. Base: frutas frescas + vegetais + sementes + pellets.",
            "en": "Frugivore/granivore. Base: fresh fruit + vegetables + seeds + pellets.",
            "fr": "Frugivore/granivore. Base: fruits frais + légumes + graines + granulés.",
            "de": "Frugivore/Körnerfresser. Basis: frisches Obst + Gemüse + Samen + Pellets."
        }
    },
    "aratinga": {
        "nome": {"pt": "Aratinga (Jandaia/Periquito-do-sol)", "en": "Aratinga Conure", "fr": "Conure Aratinga", "de": "Aratinga Sittich"},
        "peso_medio_g": 100,
        "peso_min_g": 70,
        "peso_max_g": 130,
        "k_metabolico": 78,
        "proteina_manut_pct": 14,
        "gordura_manut_pct": 5,
        "fibra_max_pct": 8,
        "calcio_mg_kg": 4500,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Frugívoro/granívoro. Base: frutas + vegetais + sementes + pellets.",
            "en": "Frugivore/granivore. Base: fruits + vegetables + seeds + pellets.",
            "fr": "Frugivore/granivore. Base: fruits + légumes + graines + granulés.",
            "de": "Frugivore/Körnerfresser. Basis: Obst + Gemüse + Samen + Pellets."
        }
    },
    "forpus": {
        "nome": {"pt": "Forpus (Tuim)", "en": "Parrotlet", "fr": "Toui", "de": "Sperlingspapagei"},
        "peso_medio_g": 30,
        "peso_min_g": 22,
        "peso_max_g": 38,
        "k_metabolico": 78,
        "proteina_manut_pct": 13,
        "gordura_manut_pct": 5,
        "fibra_max_pct": 6,
        "calcio_mg_kg": 4000,
        "fosforo_mg_kg": 3500,
        "vitamina_a_ui_kg": 8000,
        "notas": {
            "pt": "Granívoro. Base: sementes pequenas + pellets + vegetais.",
            "en": "Granivore. Base: small seeds + pellets + vegetables.",
            "fr": "Granivore. Base: petites graines + granulés + légumes.",
            "de": "Körnerfresser. Basis: kleine Samen + Pellets + Gemüse."
        }
    },
    "amazona": {
        "nome": {"pt": "Amazona (Papagaio)", "en": "Amazon Parrot", "fr": "Amazone", "de": "Amazone"},
        "peso_medio_g": 450,
        "peso_min_g": 300,
        "peso_max_g": 600,
        "k_metabolico": 78,
        "proteina_manut_pct": 12,
        "gordura_manut_pct": 4,
        "fibra_max_pct": 8,
        "calcio_mg_kg": 5000,
        "fosforo_mg_kg": 4000,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Frugívoro/granívoro. Propenso à obesidade — controlar sementes oleaginosas e nozes.",
            "en": "Frugivore/granivore. Prone to obesity — control oily seeds and nuts.",
            "fr": "Frugivore/granivore. Sujet à l'obésité — contrôler les graines oléagineuses et noix.",
            "de": "Frugivore/Körnerfresser. Neigt zu Fettleibigkeit — ölhaltige Samen und Nüsse kontrollieren."
        }
    },
    "arara": {
        "nome": {"pt": "Arara", "en": "Macaw", "fr": "Ara", "de": "Ara"},
        "peso_medio_g": 1000,
        "peso_min_g": 300,
        "peso_max_g": 1700,
        "k_metabolico": 78,
        "proteina_manut_pct": 13,
        "gordura_manut_pct": 8,
        "fibra_max_pct": 9,
        "calcio_mg_kg": 5000,
        "fosforo_mg_kg": 4000,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Frugívoro/granívoro. Necessita de gorduras saudáveis (nozes, sementes). Alta necessidade calórica.",
            "en": "Frugivore/granivore. Needs healthy fats (nuts, seeds). High caloric need.",
            "fr": "Frugivore/granivore. A besoin de graisses saines (noix, graines). Besoin calorique élevé.",
            "de": "Frugivore/Körnerfresser. Braucht gesunde Fette (Nüsse, Samen). Hoher Kalorienbedarf."
        }
    },
    "cacatua": {
        "nome": {"pt": "Cacatua", "en": "Cockatoo", "fr": "Cacatoès", "de": "Kakadu"},
        "peso_medio_g": 500,
        "peso_min_g": 300,
        "peso_max_g": 900,
        "k_metabolico": 78,
        "proteina_manut_pct": 12,
        "gordura_manut_pct": 4,
        "fibra_max_pct": 8,
        "calcio_mg_kg": 5000,
        "fosforo_mg_kg": 4000,
        "vitamina_a_ui_kg": 10000,
        "notas": {
            "pt": "Granívoro/frugívoro. Propenso à obesidade lipídica — minimizar sementes gordurosas.",
            "en": "Granivore/frugivore. Prone to lipid obesity — minimize fatty seeds.",
            "fr": "Granivore/frugivore. Sujet à l'obésité lipidique — minimiser les graines grasses.",
            "de": "Körnerfresser/Frugivore. Neigt zu Lipidübergewicht — fettige Samen minimieren."
        }
    },
}

# -------------------------------------------------------------------
# MULTIPLICADORES POR PERÍODO DE VIDA
# Fonte: Roudybush (1996), Harrison & Lightfoot (2006)
# -------------------------------------------------------------------
MULTIPLICADORES_PERIODO = {
    "manutencao": {
        "fator": 1.5,
        "proteina_extra_pct": 0,
        "nome": {"pt": "Manutenção", "en": "Maintenance", "fr": "Entretien", "de": "Erhaltung"},
        "descricao": {
            "pt": "Ave adulta saudável em atividade normal.",
            "en": "Healthy adult bird in normal activity.",
            "fr": "Oiseau adulte sain en activité normale.",
            "de": "Gesunder adulter Vogel bei normaler Aktivität."
        }
    },
    "pre_reproducao": {
        "fator": 1.8,
        "proteina_extra_pct": 2,
        "nome": {"pt": "Pré-Reprodução", "en": "Pre-Breeding", "fr": "Pré-Reproduction", "de": "Vor der Zucht"},
        "descricao": {
            "pt": "Condicionamento reprodutivo. Aumentar proteína e cálcio gradualmente.",
            "en": "Reproductive conditioning. Gradually increase protein and calcium.",
            "fr": "Conditionnement reproductif. Augmenter progressivement protéines et calcium.",
            "de": "Reproduktionskonditionierung. Protein und Calcium schrittweise erhöhen."
        }
    },
    "oviposicao": {
        "fator": 2.0,
        "proteina_extra_pct": 3,
        "nome": {"pt": "Oviposição e Incubação", "en": "Egg-laying & Incubation", "fr": "Ponte et Incubation", "de": "Eiablage & Bebrütung"},
        "descricao": {
            "pt": "Fêmea necessita de mais cálcio e proteína para formação dos ovos. Oferecer cálcio ad libitum.",
            "en": "Female needs more calcium and protein for egg formation. Offer calcium ad libitum.",
            "fr": "La femelle a besoin de plus de calcium et de protéines pour la formation des œufs.",
            "de": "Weibchen benötigt mehr Calcium und Protein für die Eierbildung."
        }
    },
    "alimentacao_filhotes": {
        "fator": 2.5,
        "proteina_extra_pct": 5,
        "nome": {"pt": "Alimentação de Filhotes", "en": "Chick Feeding", "fr": "Alimentation des Poussins", "de": "Kükenaufzucht"},
        "descricao": {
            "pt": "Pais necessitam de alta proteína para produzir pappo/leite de papo. Fornecer proteína animal (ovo cozido).",
            "en": "Parents need high protein to produce crop milk. Provide animal protein (boiled egg).",
            "fr": "Les parents ont besoin de protéines élevées pour produire le lait de jabot. Fournir des protéines animales.",
            "de": "Eltern brauchen viel Protein für Kropfmilch. Tierisches Protein (gekochtes Ei) anbieten."
        }
    },
    "muda": {
        "fator": 1.75,
        "proteina_extra_pct": 4,
        "nome": {"pt": "Muda de Penas", "en": "Moulting", "fr": "Mue", "de": "Mauser"},
        "descricao": {
            "pt": "Alta demanda de aminoácidos sulfurados (metionina, cisteína) para formação de penas. Oferecer ovos e leguminosas.",
            "en": "High demand for sulfur amino acids (methionine, cysteine) for feather formation.",
            "fr": "Forte demande en acides aminés soufrés (méthionine, cystéine) pour la formation des plumes.",
            "de": "Hoher Bedarf an Schwefelaminosäuren (Methionin, Cystein) für die Federbildung."
        }
    },
    "crescimento": {
        "fator": 2.2,
        "proteina_extra_pct": 5,
        "nome": {"pt": "Crescimento (Jovem)", "en": "Growth (Juvenile)", "fr": "Croissance (Juvénile)", "de": "Wachstum (Jungtier)"},
        "descricao": {
            "pt": "Aves jovens em crescimento necessitam de alta proteína e energia para desenvolvimento ósseo e muscular.",
            "en": "Young growing birds need high protein and energy for bone and muscle development.",
            "fr": "Les jeunes oiseaux en croissance ont besoin de protéines et d'énergie élevées.",
            "de": "Junge wachsende Vögel brauchen viel Protein und Energie für Knochen- und Muskelentwicklung."
        }
    },
}

# -------------------------------------------------------------------
# MULTIPLICADORES POR TIPO DE RECINTO (ATIVIDADE DE VOO)
# -------------------------------------------------------------------
MULTIPLICADORES_RECINTO = {
    "gaiola_pequena": {
        "fator": 1.0,
        "nome": {"pt": "Gaiola Pequena (até 60cm)", "en": "Small Cage (up to 60cm)", "fr": "Petite Cage (jusqu'à 60cm)", "de": "Kleiner Käfig (bis 60cm)"},
        "descricao": {
            "pt": "Atividade mínima. Risco de obesidade — controlar alimentos energéticos.",
            "en": "Minimal activity. Risk of obesity — control energy-dense foods.",
            "fr": "Activité minimale. Risque d'obésité — contrôler les aliments énergétiques.",
            "de": "Minimale Aktivität. Übergewichtsrisiko — energiereiche Lebensmittel kontrollieren."
        }
    },
    "gaiola_media": {
        "fator": 1.1,
        "nome": {"pt": "Gaiola Média (60–120cm)", "en": "Medium Cage (60–120cm)", "fr": "Cage Moyenne (60–120cm)", "de": "Mittelgroßer Käfig (60–120cm)"},
        "descricao": {
            "pt": "Atividade moderada. Padrão para a maioria das criações domésticas.",
            "en": "Moderate activity. Standard for most domestic breeding.",
            "fr": "Activité modérée. Standard pour la plupart des élevages domestiques.",
            "de": "Moderate Aktivität. Standard für die meiste Heimhaltung."
        }
    },
    "gaiola_grande": {
        "fator": 1.2,
        "nome": {"pt": "Gaiola Grande (120–200cm)", "en": "Large Cage (120–200cm)", "fr": "Grande Cage (120–200cm)", "de": "Großer Käfig (120–200cm)"},
        "descricao": {
            "pt": "Boa atividade física. Indicado para reprodução.",
            "en": "Good physical activity. Recommended for breeding.",
            "fr": "Bonne activité physique. Recommandé pour la reproduction.",
            "de": "Gute körperliche Aktivität. Empfohlen für die Zucht."
        }
    },
    "viveiro": {
        "fator": 1.4,
        "nome": {"pt": "Viveiro / Aviário (>200cm)", "en": "Aviary (>200cm)", "fr": "Volière (>200cm)", "de": "Voliere (>200cm)"},
        "descricao": {
            "pt": "Alta atividade. Aves voam livremente — necessidade calórica significativamente maior.",
            "en": "High activity. Birds fly freely — significantly higher caloric need.",
            "fr": "Haute activité. Les oiseaux volent librement — besoin calorique nettement plus élevé.",
            "de": "Hohe Aktivität. Vögel fliegen frei — deutlich höherer Kalorienbedarf."
        }
    },
}

# -------------------------------------------------------------------
# BASE DE DADOS DE ALIMENTOS (kcal/kg matéria seca)
# Fonte: Tabela de Composição de Alimentos (TACO/USDA) + literatura aviária
# -------------------------------------------------------------------
ALIMENTOS_BASE = [
    {"id": "pellet_manutencao",   "nome": "Pellet de Manutenção",       "kcal_kg": 3200, "proteina_pct": 14, "gordura_pct": 5,  "umidade_pct": 10},
    {"id": "pellet_reproducao",   "nome": "Pellet de Reprodução",       "kcal_kg": 3500, "proteina_pct": 20, "gordura_pct": 7,  "umidade_pct": 10},
    {"id": "milho_pipoca_cru",    "nome": "Milho de Pipoca (cru)",      "kcal_kg": 3620, "proteina_pct": 10, "gordura_pct": 4,  "umidade_pct": 12},
    {"id": "milho_verde",         "nome": "Milho Verde (cozido)",       "kcal_kg": 860,  "proteina_pct": 3,  "gordura_pct": 1,  "umidade_pct": 70},
    {"id": "alpiste",             "nome": "Alpiste",                    "kcal_kg": 3700, "proteina_pct": 14, "gordura_pct": 6,  "umidade_pct": 10},
    {"id": "painco",              "nome": "Painço",                     "kcal_kg": 3780, "proteina_pct": 11, "gordura_pct": 4,  "umidade_pct": 10},
    {"id": "girassol_sem_casca",  "nome": "Girassol (sem casca)",       "kcal_kg": 5840, "proteina_pct": 21, "gordura_pct": 51, "umidade_pct": 5},
    {"id": "amendoim_sem_sal",    "nome": "Amendoim (sem sal, cru)",    "kcal_kg": 5670, "proteina_pct": 26, "gordura_pct": 49, "umidade_pct": 6},
    {"id": "noz_sem_sal",         "nome": "Noz (sem sal)",              "kcal_kg": 6540, "proteina_pct": 15, "gordura_pct": 65, "umidade_pct": 4},
    {"id": "cenoura_crua",        "nome": "Cenoura (crua)",             "kcal_kg": 410,  "proteina_pct": 1,  "gordura_pct": 0,  "umidade_pct": 88},
    {"id": "brocolis",            "nome": "Brócolis (cru)",             "kcal_kg": 340,  "proteina_pct": 3,  "gordura_pct": 0,  "umidade_pct": 89},
    {"id": "espinafre",           "nome": "Espinafre (cru)",            "kcal_kg": 230,  "proteina_pct": 3,  "gordura_pct": 0,  "umidade_pct": 91},
    {"id": "maca",                "nome": "Maçã (sem semente)",         "kcal_kg": 520,  "proteina_pct": 0,  "gordura_pct": 0,  "umidade_pct": 86},
    {"id": "banana",              "nome": "Banana",                     "kcal_kg": 890,  "proteina_pct": 1,  "gordura_pct": 0,  "umidade_pct": 75},
    {"id": "manga",               "nome": "Manga",                      "kcal_kg": 600,  "proteina_pct": 1,  "gordura_pct": 0,  "umidade_pct": 83},
    {"id": "mamao",               "nome": "Mamão",                      "kcal_kg": 430,  "proteina_pct": 1,  "gordura_pct": 0,  "umidade_pct": 88},
    {"id": "ovo_cozido",          "nome": "Ovo Cozido (inteiro)",       "kcal_kg": 1550, "proteina_pct": 13, "gordura_pct": 11, "umidade_pct": 75},
    {"id": "feijao_cozido",       "nome": "Feijão Cozido",              "kcal_kg": 770,  "proteina_pct": 9,  "gordura_pct": 0,  "umidade_pct": 65},
    {"id": "arroz_cozido",        "nome": "Arroz Cozido",               "kcal_kg": 1300, "proteina_pct": 3,  "gordura_pct": 0,  "umidade_pct": 68},
    {"id": "aveia",               "nome": "Aveia em Flocos",            "kcal_kg": 3890, "proteina_pct": 17, "gordura_pct": 7,  "umidade_pct": 10},
    {"id": "mix_sementes_peq",    "nome": "Mix de Sementes (pequenas)", "kcal_kg": 3500, "proteina_pct": 13, "gordura_pct": 8,  "umidade_pct": 10},
    {"id": "quinoa_cozida",       "nome": "Quinoa (cozida)",            "kcal_kg": 1200, "proteina_pct": 4,  "gordura_pct": 2,  "umidade_pct": 72},
    {"id": "calcario_osso_lula",  "nome": "Osso de Lula / Cálcario",   "kcal_kg": 0,    "proteina_pct": 0,  "gordura_pct": 0,  "umidade_pct": 5},
]


def calcular_tmb(peso_g, k=78):
    """
    Taxa Metabólica Basal para psitacídeos.
    TMB = K * (Peso em kg)^0.75
    """
    peso_kg = peso_g / 1000.0
    return k * (peso_kg ** 0.75)


def calcular_necessidades(especie, peso_g, periodo, tipo_recinto):
    """
    Calcula as necessidades nutricionais diárias completas.
    Retorna dict com todos os valores calculados.
    """
    if especie not in ESPECIES_DADOS:
        return {"erro": "Espécie não encontrada"}

    dados_esp = ESPECIES_DADOS[especie]
    mult_periodo = MULTIPLICADORES_PERIODO.get(periodo, MULTIPLICADORES_PERIODO["manutencao"])
    mult_recinto = MULTIPLICADORES_RECINTO.get(tipo_recinto, MULTIPLICADORES_RECINTO["gaiola_media"])

    # TMB e Energia Metabolizável Diária
    tmb = calcular_tmb(peso_g, dados_esp["k_metabolico"])
    fator_total = mult_periodo["fator"] * mult_recinto["fator"]
    kcal_dia = round(tmb * fator_total, 1)

    # Necessidades de macronutrientes (em g/dia)
    proteina_pct = dados_esp["proteina_manut_pct"] + mult_periodo["proteina_extra_pct"]
    gordura_pct = dados_esp["gordura_manut_pct"]

    # Assumindo 4 kcal/g proteína, 9 kcal/g gordura, 4 kcal/g carboidrato
    proteina_g = round((kcal_dia * proteina_pct / 100) / 4, 1)
    gordura_g = round((kcal_dia * gordura_pct / 100) / 9, 1)

    # Água: aproximadamente 50ml por kg de peso vivo ao dia (manutenção)
    # Aumenta 20% na reprodução, muda e alimentação de filhotes
    agua_base_ml = (peso_g / 1000.0) * 50
    fatores_agua = {"oviposicao": 1.3, "alimentacao_filhotes": 1.4, "muda": 1.2}
    fator_agua = fatores_agua.get(periodo, 1.0)
    agua_ml = round(agua_base_ml * fator_agua * mult_recinto["fator"], 1)

    # Quantidade total de alimento (base matéria seca) em g/dia
    # Estimativa: aves consomem ~10-15% do peso corporal em alimento fresco/dia
    # Ajustado pelo período e recinto
    alimento_total_g = round(peso_g * 0.10 * mult_periodo["fator"] * mult_recinto["fator"], 1)

    # Cálcio e fósforo (mg/dia)
    calcio_mg = round((dados_esp["calcio_mg_kg"] / 1000) * (alimento_total_g / 1000), 2)
    fosforo_mg = round((dados_esp["fosforo_mg_kg"] / 1000) * (alimento_total_g / 1000), 2)

    return {
        "especie": dados_esp["nome"],
        "peso_g": peso_g,
        "tmb_kcal": round(tmb, 1),
        "fator_periodo": mult_periodo["fator"],
        "fator_recinto": mult_recinto["fator"],
        "fator_total": round(fator_total, 2),
        "kcal_dia": kcal_dia,
        "proteina_pct": proteina_pct,
        "proteina_g_dia": proteina_g,
        "gordura_pct": gordura_pct,
        "gordura_g_dia": gordura_g,
        "agua_ml_dia": agua_ml,
        "alimento_total_g": alimento_total_g,
        "calcio_mg_dia": calcio_mg,
        "fosforo_mg_dia": fosforo_mg,
        "periodo_nome": mult_periodo["nome"],
        "periodo_descricao": mult_periodo["descricao"],
        "recinto_nome": mult_recinto["nome"],
        "recinto_descricao": mult_recinto["descricao"],
        "notas_especie": dados_esp["notas"],
        "fibra_max_pct": dados_esp["fibra_max_pct"],
    }


def calcular_porcao_alimento(kcal_dia, alimento_id=None, kcal_kg_custom=None,
                              nome_custom=None, umidade_pct=0):
    """
    Calcula a porção diária de um alimento específico.
    Considera a umidade para converter para matéria fresca.
    """
    if alimento_id:
        alimento = next((a for a in ALIMENTOS_BASE if a["id"] == alimento_id), None)
        if not alimento:
            return None
        kcal_kg = alimento["kcal_kg"]
        umidade = alimento["umidade_pct"]
        nome = alimento["nome"]
        proteina_pct = alimento["proteina_pct"]
        gordura_pct = alimento["gordura_pct"]
    else:
        kcal_kg = kcal_kg_custom or 3000
        umidade = umidade_pct
        nome = nome_custom or "Alimento customizado"
        proteina_pct = 0
        gordura_pct = 0

    if kcal_kg == 0:
        return {
            "nome": nome,
            "quantidade_g": "Ad libitum",
            "kcal_fornecidas": 0,
            "proteina_g": 0,
            "gordura_g": 0,
            "nota": "Suplemento mineral — oferecer à vontade"
        }

    # Ajuste pela umidade: kcal_kg já é referente ao alimento como oferecido
    quantidade_g = round((kcal_dia / kcal_kg) * 1000, 1)
    kcal_fornecidas = round(quantidade_g * kcal_kg / 1000, 1)
    proteina_g = round(quantidade_g * proteina_pct / 100, 1)
    gordura_g = round(quantidade_g * gordura_pct / 100, 1)

    return {
        "nome": nome,
        "quantidade_g": quantidade_g,
        "kcal_fornecidas": kcal_fornecidas,
        "proteina_g": proteina_g,
        "gordura_g": gordura_g,
        "umidade_pct": umidade,
        "nota": ""
    }


def get_alimentos():
    return ALIMENTOS_BASE


def get_especies_alimentacao():
    return {k: v["nome"] for k, v in ESPECIES_DADOS.items()}