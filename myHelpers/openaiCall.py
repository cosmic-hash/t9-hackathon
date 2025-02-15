from openai import OpenAI


class OpenAIHandler:
    def __init__(self):
        self.client = OpenAI()

    def send_to_openai(self, purpose, user_query=None):
        # Construct the user prompt based on provided query or default prompt
        if user_query:
            user_prompt = (
                f"Here is a medicine purpose: '{purpose}'. User's query: '{user_query}'. "
                "Please provide a clear, knowledgeable, and concise answer strictly based on the provided purpose without relying on any external knowledge. Avoid formatting like bold text; use plain text with numbers and decimals as needed."
            )
        else:
            user_prompt = (
                f"Here is a medicine purpose: '{purpose}'. Can you briefly explain what condition this medicine is meant to treat and how it helps? "
                "Please use only the provided content and do not rely on any external knowledge. Keep the response concise, clear, and in plain text without special formatting."
            )

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and concise assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content


def explain_drug_from_json(fda_json, user_query=None):
    """
    Function to explain the problems solved by a drug based on FDA drug JSON response.

    Parameters:
        fda_json (dict): The JSON response containing drug details.
        user_query (str): Optional user query for custom prompt.

    Returns:
        str: The explanation of the problems the drug solves.
    """
    # Extract all information from the JSON response
    all_info = []
    for key, value in fda_json["results"][0].items():
        all_info.append(f"{key}: {value}")

    purpose = "\n".join(all_info)

    # Instantiate the OpenAI handler and get the explanation
    handler = OpenAIHandler()
    explanation = handler.send_to_openai(purpose, user_query)
    return explanation



# Example usage
fda_json = {
    "meta": {
        "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
        "terms": "https://open.fda.gov/terms/",
        "license": "https://open.fda.gov/license/",
        "last_updated": "2025-02-15",
        "results": {"skip": 0, "limit": 1, "total": 105},
    },
    "results": [
        {
            "spl_product_data_elements": [
                "Hydralazine Hydrochloride Hydralazine Hydrochloride Hydralazine Hydrochloride HYDRALAZINE MICROCRYSTALLINE CELLULOSE 102 MICROCRYSTALLINE CELLULOSE 105 SODIUM STARCH GLYCOLATE TYPE A POTATO SILICON DIOXIDE MAGNESIUM STEARATE FD&C YELLOW NO. 6 Peach EP;102"
            ],
            "description": [
                "DESCRIPTION HydrALAZINE hydrochloride, USP, is an antihypertensive, for oral administration. Its chemical name is 1-hydrazinophthalazine monohydrochloride, and its structural formula is: HydrALAZINE hydrochloride, USP is a white to off-white, odorless crystalline powder. It is soluble in water, slightly soluble in alcohol, and very slightly soluble in ether. It melts at about 275°C, with decomposition. Each tablet for oral administration contains 25 mg hydrALAZINE hydrochloride, USP. Tablets also contain magnesium stearate, microcrystalline cellulose, orange lake blend, silicon dioxide, and sodium starch glycolate. The orange lake blend consists of FD&C yellow #6. chemical-structure"
            ],
            "clinical_pharmacology": [
                "CLINICAL PHARMACOLOGY Although the precise mechanism of action of hydrALAZINE is not fully understood, the major effects are on the cardiovascular system. HydrALAZINE apparently lowers blood pressure by exerting a peripheral vasodilating effect through a direct relaxation of vascular smooth muscle. HydrALAZINE, by altering cellular calcium metabolism, interferes with the calcium movements within the vascular smooth muscle that are responsible for initiating or maintaining the contractile state. The peripheral vasodilating effect of hydrALAZINE results in decreased arterial blood pressure (diastolic more than systolic); decreased peripheral vascular resistance; and an increased heart rate, stroke volume, and cardiac output. The preferential dilatation of arterioles, as compared to veins, minimizes postural hypotension and promotes the increase in cardiac output. HydrALAZINE usually increases renin activity in plasma, presumably as a result of increased secretion of renin by the renal juxtaglomerular cells in response to reflex sympathetic discharge. This increase in renin activity leads to the production of angiotensin II, which then causes stimulation of aldosterone and consequent sodium reabsorption. HydrALAZINE also maintains or increases renal and cerebral blood flow. HydrALAZINE is rapidly absorbed after oral administration, and peak plasma levels are reached at 1 to 2 hours. Plasma levels of apparent hydrALAZINE decline with a half-life of 3 to 7 hours. Binding to human plasma protein is 87%. Plasma levels of hydrALAZINE vary widely among individuals. HydrALAZINE is subject to polymorphic acetylation; slow acetylators generally have higher plasma levels of hydrALAZINE and require lower doses to maintain control of blood pressure. HydrALAZINE undergoes extensive hepatic metabolism; it is excreted mainly in the form of metabolites in the urine."
            ],
            "indications_and_usage": [
                "INDICATIONS AND USAGE Essential hypertension, alone or as an adjunct."
            ],
            "contraindications": [
                "CONTRAINDICATIONS Hypersensitivity to hydrALAZINE; coronary artery disease; mitral valvular rheumatic heart disease."
            ],
            "warnings": [
                "WARNINGS ​ In a few patients hydrALAZINE may produce a clinical picture simulating systemic lupus erythematosus including glomerulonephritis. In such patients hydrALAZINE should be discontinued unless the benefit-to-risk determination requires continued antihypertensive therapy with this drug. Symptoms and signs usually regress when the drug is discontinued but residua have been detected many years later. Long-term treatment with steroids may be necessary. (See PRECAUTIONS, Laboratory Tests .)"
            ],
            "precautions": [
                "PRECAUTIONS General Myocardial stimulation produced by hydrALAZINE can cause anginal attacks and ECG changes of myocardial ischemia. The drug has been implicated in the production of myocardial infarction. It must, therefore, be used with caution in patients with suspected coronary artery disease. The “hyperdynamic” circulation caused by hydrALAZINE may accentuate specific cardiovascular inadequacies. For example, hydrALAZINE may increase pulmonary artery pressure in patients with mitral valvular disease. The drug may reduce the pressor responses to epinephrine. Postural hypotension may result from hydrALAZINE but is less common than with ganglionic blocking agents. It should be used with caution in patients with cerebral vascular accidents. In hypertensive patients with normal kidneys who are treated with hydrALAZINE, there is evidence of increased renal blood flow and a maintenance of glomerular filtration rate. In some instances where control values were below normal, improved renal function has been noted after administration of hydrALAZINE. However, as with any antihypertensive agent, hydrALAZINE should be used with caution in patients with advanced renal damage. Peripheral neuritis, evidenced by paresthesia, numbness, and tingling, has been observed. Published evidence suggests an antipyridoxine effect, and that pyridoxine should be added to the regimen if symptoms develop. Information for Patients Patients should be informed of possible side effects and advised to take the medication regularly and continuously as directed. Laboratory Tests Complete blood counts and antinuclear antibody titer determinations are indicated before and periodically during prolonged therapy with hydrALAZINE even though the patient is asymptomatic. These studies are also indicated if the patient develops arthralgia, fever, chest pain, continued malaise, or other unexplained signs or symptoms. A positive antinuclear antibody titer requires that the physician carefully weigh the implications of the test results against the benefits to be derived from antihypertensive therapy with hydrALAZINE. Blood dyscrasias, consisting of reduction in hemoglobin and red cell count, leukopenia, agranulocytosis, and purpura, have been reported. If such abnormalities develop, therapy should be discontinued. Drug/Drug Interactions MAO inhibitors should be used with caution in patients receiving hydrALAZINE. When other potent parenteral antihypertensive drugs, such as diazoxide, are used in combination with hydrALAZINE, patients should be continuously observed for several hours for any excessive fall in blood pressure. Profound hypotensive episodes may occur when diazoxide injection and hydrALAZINE are used concomitantly. Drug/Food Interactions Administration of hydrALAZINE with food results in higher plasma levels. Carcinogenesis, Mutagenesis, Impairment of Fertility In a lifetime study in Swiss albino mice, there was a statistically significant increase in the incidence of lung tumors (adenomas and adenocarcinomas) of both male and female mice given hydrALAZINE continuously in their drinking water at a dosage of about 250 mg/kg per day (about 80 times the maximum recommended human dose). In a 2-year carcinogenicity study of rats given hydrALAZINE by gavage at dose levels of 15, 30, and 60 mg/kg/day (approximately 5 to 20 times the recommended human daily dosage), microscopic examination of the liver revealed a small, but statistically significant, increase in benign neoplastic nodules in male and female rats from the high-dose group and in female rats from the intermediate-dose group. Benign interstitial cell tumors of the testes were also significantly increased in male rats from the high-dose group. The tumors observed are common in aged rats and a significantly increased incidence was not observed until 18 months of treatment. HydrALAZINE was shown to be mutagenic in bacterial systems (Gene Mutation and DNA Repair) and in one of two rats and one rabbit hepatocyte in vitro DNA repair studies. Additional in vivo and in vitro studies using lymphoma cells, germinal cells, and fibroblasts from mice, bone marrow cells from chinese hamsters and fibroblasts from human cell lines did not demonstrate any mutagenic potential for hydrALAZINE. The extent to which these findings indicate a risk to man is uncertain. While longterm clinical observation has not suggested that human cancer is associated with hydrALAZINE use, epidemiologic studies have so far been insufficient to arrive at any conclusions. Pregnancy Teratogenic Effects Pregnancy Category C Animal studies indicate that hydrALAZINE is teratogenic in mice at 20 to 30 times the maximum daily human dose of 200 to 300 mg and possibly in rabbits at 10 to 15 times the maximum daily human dose, but that it is nonteratogenic in rats. Teratogenic effects observed were cleft palate and malformations of facial and cranial bones. There are no adequate and well-controlled studies in pregnant women. Although clinical experience does not include any positive evidence of adverse effects on the human fetus, hydrALAZINE should be used during pregnancy only if the expected benefit justifies the potential risk to the fetus. Nursing Mothers Hydralazine has been shown to be excreted in breast milk. Pediatric Use Safety and effectiveness in pediatric patients have not been established in controlled clinical trials, although there is experience with the use of hydrALAZINE in pediatric patients. The usual recommended oral starting dosage is 0.75 mg/kg of body weight daily in four divided doses. Dosage may be increased gradually over the next 3 to 4 weeks to a maximum of 7.5 mg/kg or 200 mg daily."
            ],
            "adverse_reactions": [
                "ADVERSE REACTIONS Adverse reactions with hydrALAZINE are usually reversible when dosage is reduced. However, in some cases it may be necessary to discontinue the drug. The following adverse reactions have been observed, but there has not been enough systematic collection of data to support an estimate of their frequency. Common Headache, anorexia, nausea, vomiting, diarrhea, palpitations, tachycardia, angina pectoris. Less Frequent: Digestive: constipation, paralytic ileus. Cardiovascular: hypotension, paradoxical pressor response, edema. Respiratory: dyspnea. Neurologic: peripheral neuritis, evidenced by paresthesia, numbness, and tingling; dizziness; tremors; muscle cramps; psychotic reactions characterized by depression, disorientation, or anxiety. Genitourinary: difficulty in urination. Hematologic: blood dyscrasias, consisting of reduction in hemoglobin and red cell count, leukopenia, agranulocytosis, purpura; lymphadenopathy; splenomegaly. Hypersensitive Reactions: rash, urticaria, pruritus, fever, chills, arthralgia, eosinophilia, and rarely, hepatitis. Other: nasal congestion, flushing, lacrimation, conjunctivitis."
            ],
            "overdosage": [
                "OVERDOSAGE Acute Toxicity: No deaths due to acute poisoning have been reported. Highest known dose survived: adults, 10 g orally. Oral LD 50 in rats: 173 and 187 mg/kg. Signs and Symptoms Signs and symptoms of overdosage include hypotension, tachycardia, headache, and generalized skin flushing. Complications can include myocardial ischemia and subsequent myocardial infarction, cardiac arrhythmia, and profound shock. Treatment There is no specific antidote. The gastric contents should be evacuated, taking adequate precautions against aspiration and for protection of the airway. An activated charcoal slurry may be instilled if conditions permit. These manipulations may have to be omitted or carried out after cardiovascular status has been stabilized, since they might precipitate cardiac arrhythmias or increase the depth of shock. Support of the cardiovascular system is of primary importance. Shock should be treated with plasma expanders. If possible, vasopressors should not be given, but if a vasopressor is required, care should be taken not to precipitate or aggravate cardiac arrhythmia. Tachycardia responds to beta blockers. Digitalization may be necessary, and renal function should be monitored and supported as required. No experience has been reported with extracorporeal or peritoneal dialysis."
            ],
            "dosage_and_administration": [
                "DOSAGE AND ADMINISTRATION Initiate therapy in gradually increasing dosages; adjust according to individual response. Start with 10 mg four times daily for the first 2 to 4 days, increase to 25 mg four times daily for the balance of the first week. For the second and subsequent weeks, increase dosage to 50 mg four times daily. For maintenance, adjust dosage to the lowest effective levels. The incidence of toxic reactions, particularly the L.E. cell syndrome, is high in the group of patients receiving large doses of hydrALAZINE hydrochloride tablets. In a few resistant patients, up to 300 mg of hydrALAZINE hydrochloride tablets daily may be required for a significant antihypertensive effect. In such cases, a lower dosage of hydrALAZINE hydrochloride tablets combined with a thiazide and/or reserpine or a beta blocker may be considered. However, when combining therapy, individual titration is essential to ensure the lowest possible therapeutic dose of each drug."
            ],
            "how_supplied": [
                "HOW SUPPLIED HydrALAZINE Hydrochloride Tablets, USP are available as: 25 mg – Round, peach, core tablet, debossed EP over 102 on one side and plain on the reverse side. NDC 82804-081-30 Bottles of 30 NDC 82804-081-60 Bottles of 60 NDC 82804-081-90 Bottles of 90 Dispense in a tight, light-resistant container as defined in the USP. Store at 20° to 25°C (68° to 77°F) [See USP Controlled Room Temperature]. KEEP THIS AND ALL MEDICATIONS OUT OF THE REACH OF CHILDREN. Distributed by: Avet Pharmaceuticals Inc. East Brunswick, NJ 08816 1-866-901-DRUG (3784) 51U000000426US01 Repackaged by: Proficient Rx LP Thousand Oaks, CA 91320 Revised: 11/2022 avet-logo"
            ],
            "package_label_principal_display_panel": [
                "PACKAGE LABEL.PRINCIPAL DISPLAY PANEL - 25 mg NDC 82804- 081 -30 HydrALAZINE Hydrochloride Tablets, USP 25 mg 30 Tablets Rx only ​ 82804-081-30"
            ],
            "set_id": "024ac6b8-5ce0-4435-9b11-b1806c511d7b",
            "id": "024ac6b8-5ce0-4435-9b11-b1806c511d7b",
            "effective_time": "20240301",
            "version": "1",
            "openfda": {
                "application_number": ["ANDA040858"],
                "brand_name": ["Hydralazine Hydrochloride"],
                "generic_name": ["HYDRALAZINE HYDROCHLORIDE"],
                "manufacturer_name": ["Proficient Rx LP"],
                "product_ndc": ["82804-081"],
                "product_type": ["HUMAN PRESCRIPTION DRUG"],
                "route": ["ORAL"],
                "substance_name": ["HYDRALAZINE HYDROCHLORIDE"],
                "rxcui": ["905225"],
                "spl_id": ["024ac6b8-5ce0-4435-9b11-b1806c511d7b"],
                "spl_set_id": ["024ac6b8-5ce0-4435-9b11-b1806c511d7b"],
                "package_ndc": ["82804-081-30", "82804-081-60", "82804-081-90"],
                "original_packager_product_ndc": ["23155-833"],
                "upc": ["0382804081301"],
                "unii": ["FD171B778Y"],
            },
        }
    ],
}

# Get and print the explanation
# explanation = explain_drug_from_json(fda_json)
# print(explanation)
