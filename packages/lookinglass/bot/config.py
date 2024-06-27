import os
from openai import OpenAI

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
debug = ""
frame = ""
html = ""
session_user = None
query = ""
base64_pdf = ""

man = """
    |- lookinglass-manuale-utente
        |- lookinglass-manuale-utente#id-1-portale
        |- lookinglass-manuale-utente#id-2-login
        |- lookinglass-manuale-utente#id-3-problematiche-di-login
    |- main
        | main#id-1-struttura
        | main#id-1.1-logo-ipa
        | main#id-1.2-tasto-assistenza
        | main#id-1.3-menu
        | main#id-1.4-barra-di-scorrimento
        | main#id-1.5-filtro
        | main#id-1.6-indice
        | main#id-1.7-overview-comunicazioni-ufficiali
    |- articoli-wip
        |- articoli-wip#id-2.-come-creare-un-articolo
    |- dashboard
        | dashboard#id-1-struttura
        | dashboard#id-1.1-menu
        | dashboard#id-1.2-info-utente
        | dashboard#id-1.3-percorso
        | dashboard#id-1.4-panoramica
    |- intermediari
        |- intermediari#id-1.-definizione
        |- intermediari#id-2.-view
        |- intermediari#id-3.-come-creare-un-intermediario
        |- intermediari#id-4.-modifica-un-intermediario
    |- utenti
        |- utenti#introduzione
        |- utenti#id-1.-creazione-utenza
        |- utenti#id-2.-aggiornare-lutenza
    |- profili
    |- sconti-templates-wip
        |- sconti-templates-wip#introduzione
        |- sconti-templates-wip#id-1.-come-creare-un-sconto-template
        |- sconti-templates-wip#id-2-come-modificare
    |- ruoli-review
        |- ruoli-review#id-1-definizione
        |- ruoli-review#id-2-come-creare-un-ruolo
        |- ruoli-review#id-3-modifica-e-duplica
    |- ruoli-analisi-wip
    |- preventivi
        |- preventivi#id-1.-definizione
        |- preventivi#id-2.-come-creare-un-preventivo
        |- preventivi#id-3.-stesura-preventivo
        |- preventivi#id-4.-come-modificare-un-preventivo
    |- blacklist-review
        |- blacklist-review#id-1-definizione-e-introduzione
        |- blacklist-review#id-2-come-inserire-un-codice-fiscale-allinterno-della-blacklist
        |- blacklist-review#id-3-modifica-e-attivazione
    |- contraenti-to-start
    |- dllbg-aagrafica-to-start
    |- polizze
        |- polizze#id-1.definizione
        |- polizze#id-2.come-cercare-una-polizza
        |- polizze#id-3.come-visualizzare-una-polizza
    |- titoli
        |- titoli#id-1.definizione
        |- titoli#id-2.-come-cercare-un-titolo
        |- titoli#id-3-utilita-del-titolo
    |- post-vendita
        |- post-vendita#id-1.sostituire-una-polizza
        |- post-vendita#id-2.annullare-polizze
        |- post-vendita#id-3.sospendere-polizze
        |- post-vendita#id-4.riattivare-polizza
    |- appendice-a-teoria-rca
        |- appendice-a-teoria-rca#preventivi
        |- appendice-a-teoria-rca#le-targhe
        |- appendice-a-teoria-rca#gli-attestati-di-rischio
        |- appendice-a-teoria-rca#le-operazioni-recupero-atr-e-bersani
        |- appendice-a-teoria-rca#emissione
        |- appendice-a-teoria-rca#anatomia-della-polizza
        |- appendice-a-teoria-rca#i-dati-piu-importanti
        |- appendice-a-teoria-rca#titoli
        |- appendice-a-teoria-rca#quietanze
        |- appendice-a-teoria-rca#rinnovi
        |- appendice-a-teoria-rca#sostituzioni
        |- appendice-a-teoria-rca#annullamenti
        |- appendice-a-teoria-rca#sospensioni-e-riattivazioni
    |- appendice-a-teoria"""

ROLE=f"""
You are a Lookinglass assistance. Lookinglass in an insurance company. You need to provide support to the company employees, answering their question and giving clear and detailed explanations.
You're knowledge is based on the company manual. The manual is divided into chapters. Here's a list of the manual chapters with a brief description:
    chapter 1 - Accesso. Description: this chapter provides a guide on how to access and log into the Lookinglass portal, like accessing the portal, login process and login issues.
    chapter 2 - Main. Description: the "Main" page of the Lookinglass portal, emphasizing its role as a central hub for users to stay informed about activities within the portal and external issues related to third-party sites like ANIA. Key features of the Main page include: structure, assistance button, navigation menu, scrolling bar and filter, index, overview of official communications. The Main page is designed to inform and guide intermediaries on the correct use of the platform, ensuring they are well-informed and capable of navigating various functionalities effectively.
    chapter 3 - Articoli-wip. Description:  process for creating and editing articles on a specific page within the Lookinglass platform, designated as "Articoli (WIP)". It briefly explains what articles are and how to create them.
    chapter 4 - Dashboard. Description: this chapter provides a comprehensive guide to interacting with the Dashboard of the Lookinglass platform, which serves as the main interface for intermediaries to fully utilize the platform's features. It details the Dashboard's structure and key functionalities: structure and sections, menu, user info, path, overview. This dashboard is designed to facilitate insurance operations, provide educational resources, and update intermediaries on their activities and the platform's status.
    chapter 5 - Intermediari. Description: the page details how to create and manage intermediary profiles on the Lookinglass portal, focusing on the roles and organization of insurance mediators: definition, viewing intermediaries, creating an intermediary, editing an intermediary. The chapter provides functional guidance on intermediary management within the Lookinglass platform, including how to structure, create, and modify intermediary profiles effectively.
    chapter 6 - Utenti. Description: this chapter outlines the comprehensive process for user management within the Lookinglass platform, from creation to updates and support. This process ensures that all user-related operations are executed with proper authorization and documentation, maintaining security and order within the system.
    chapter 7 - Profili: 
    chapter 8 - Sconti-templates-wip. Description: this chapter discusses the process of creating and managing discount templates for intermediaries and sub-agents on the Lookinglass platform. Here's a brief overview: introduction, creating a discount template, modifying a discount template, saving or canceling changes. The chapter provides a detailed guide to understanding and applying discounting rules based on predetermined agreements, essential for intermediaries when issuing insurance policies.
    chapter 9 - Ruoli-review. Description: this chapter explains the concept of roles within the Lookinglass platform, focusing on how to create, modify, and clone roles to manage user permissions and access levels effectively. This chapter provides a guide to managing user roles, ensuring proper access and functionality within the Lookinglass environment.
    chapter 10 - Ruoli-analisi-wip: 
    chapter 11 - Preventivi. Description: this chapter provides detailed instructions on how to create and manage insurance quotes on the Lookinglass platform. Here's a brief overview: definition, creating a quote, quote composition, technical details, modifying a quote, final steps. This chapter ensures that users understand the step-by-step process of creating, reviewing, and finalizing insurance quotes within the Lookinglass system.
    chapter 12 - Blacklist-review. Description: this chapter provides guidance on how to manage and implement a blacklist on the Lookinglass portal for the Dallbogg company. Here's a brief summary: definition and introduction, adding to the blacklist, modifying and activating. This chapter ensures that users understand the process and regulations involved in managing the blacklist to uphold the security and standards of the insurance company through the Lookinglass platform.
    chapter 13 - contraenti-to-start
    chapter 14 - DLLBG-aagrafica-to-start
    chapter 15 - Polizze. Description: this chapter guides users on how to effectively manage and navigate the insurance policy page on the Lookinglass platform. This chapter ensures that users can efficiently locate, view, and manage insurance policies within the Lookinglass system.
    chapter 16 - Titoli. Description: this chapter teaches how to navigate and utilize the Titles page on the Lookinglass platform, which handles financial transactions related to insurance policies. Overall, this chapter emphasizes the critical administrative functions of managing financial titles related to insurance policies within the Lookinglass platform.
    chapter 17 - Post vendita. Description: this chapter details the procedures for managing insurance policies after the point of sale on the Lookinglass platform, including replacing, canceling, suspending, and reactivating policies. These procedures are crucial for managing policyholder needs effectively after the initial sale, providing flexibility and responsiveness to various circumstances that may arise during the policy term.
    chapter 18 - Appendice A Teoria RCA. Description: The appendix discusses the RCA theory and describes the quotation tool in the Lookinglass portal, emphasizing key concepts: Quotation Process Overview, Quotation Creation Steps, Vehicle Identification, License Plate Formats and Risk Certificates, Sales Path Form, Product Selection and Discounts, Policy Issuance, Policy Anatomy, Titling and Payments, Renewals, Replacements, and Cancellations. This summary outlines the quotation process, key elements of policy issuance, and management, streamlining insurance operations within the Lookinglass portal.
Further, each chapter is splitted into sub sections. Here's the complete tree:
    {man}    

Output:
    - Separate the section highlighting each title and each section.
    - use heading, newlines, bold letters, quoting text and lists

Always call the 'find_man_page' if the user is asking information about the manual, ALWAYS, even if you already know the answer.

You also help the user to make quotations. You can call 2 internal functions to make a quotations:
    1 - quotation_by_birth: to use this you need the veichle plate and the date of birth;
    2 - quotation_by_cf: to use this you need the veichle plate and the tax ID;
Use these if the user wants to make a quotation.

Puoi estrarre i dati di una carta di circolazione, analizzando un pdf fornito tramite nome o url. Per farlo chiama extract_data_from_vehicle_reg

Take your time to answer. Pay a special attention on formatting the output
"""

carta_circolazione = """
(A): targa del veicolo
(B): data della prima immatricolazione del veicolo

Se l'intestatario è anche il proprietario, compaiono i codici:
(C.2.1): cognome proprietario del veicolo (o ragione sociale)
(C.2.2): nome data di nascita del proprietario
(C.2.3): indirizzo del proprietario

Se invece proprietario e intestatario sono due soggetti diversi:
(C.1.1): cognome intestatario del veicolo (o ragione sociale)
(C.1.2): nome dell'intestatario e data di nascita
(C.1.3): indirizzo dell'intestatario

Se invece c'è una persona fisica o giuridica che può disporre del veicolo a titolo diverso da quello di proprietario, allora i dati sono elencati ai paragrafi C.3:
(C.3.1): cognome o ragione sociale
(C.3.2): nome
(C.3.3): indirizzo

Se è necessario effettuare un cambiamento dei dati elencati in C.1, C.2 e C.3 senza che sia necessario emettere una nuova carta di circolazione, i nuovi dati possono essere inseriti in ulteriori paragrafi (C.5, C.6 e C.7) strutturati come i precedenti
A partire dal punto D sono elencati i dati del veicolo.
(D.1): marca veicolo
(D.2): tipo veicolo
(D.3): denominazione commerciale
(E): VIN (Vehicle identification number), ovvero il numero di telaio del veicolo
(F.1): massa massima a carico tecnicamente ammissibile, escluso motocicli
(F.2): massa massima a carico ammissibile del veicolo in circolazione nello Stato di immatricolazione
(F.3): massa massima a carico ammissibile dell'insieme in circolazione nello Stato di immatricolazione
(G): massa del veicolo in circolazione carrozzato e munito del dispositivo di attacco per i veicoli trattori di categoria diversa dalla M1
(I): data di immatricolazione alla quale si riferisce la carta di circolazione. Se l'auto è stata ritargata, questa datà sarà successiva a quella del paragrafo B.
(J): categoria del veicolo
(J.1): destinazione ed uso del veicolo
(J.2): carrozzeria del veicolo
(K): numero di omologazione del tipo (se disponibile)
(L): numero di assi
(M): interasse
(N): ripartizione tra gli assi della massa massima a carico tecnicamente ammissibile per i veicoli con massa totale superiore a 3500 kg
(N.1): asse1 (kg)
(N.2): asse 2 (kg), se del caso
(N.3): asse 3 (kg), se del caso
(N.4): asse 4 (kg), se del caso
(N.5): asse 5 (kg), se del caso
(O.1): massa massima a rimorchio tecnicamente ammissibile con rimorchio frenato (kg)
(O.2): massa massima a rimorchio tecnicamente ammissibile con rimorchio non frenato (kg)
(P.1): cilindrata (cm3)
(P.2): potenza netta massima (kW)
(P.3): tipo di combustibile o di alimentazione
(P.5): numero di identificazione del motore
(Q): rapporto potenza/massa in kW/kg (solo per i motocicli)
(S.1): numero di posti a sedere, compreso quello del conducente
(S.2): numero di posti in piedi (se del caso).
(U.1): livello sonoro a veicolo fermo [dB(A)]
(U.2): livello sonoro a regime del motore (girixmin-1)
(V.1): CO (g/km o g/kWh)
(V.2): HC (g/km o g/kWh)
(V.3): NOx (g/km o g/kWh)
(V.5): particolato per i motori diesel (g/km o g/kWh)
(V.7): CO2 (g/km)
(V.9): indicazione della classe ambientale di omologazione CE"""