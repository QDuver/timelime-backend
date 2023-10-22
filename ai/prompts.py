def get_timeline_prompts(n_events, timeline_name):
    return {
    'en': ['''
       Response has to be in JSON format. Each object represents an event, with the following format: name, description, startDate, endDate, endDate being optional.
      Dates can be in YYYY-MM-DD or YYYY-MM or YYYY format.
      Never write the dates with BC, AD, CE, BCE, ABY, BBY, etc. If they are negative, just put a minus sign before the year.
      Escape all double quotes with a backslash.
    ''',
    f'''Generate a historic timeline of {timeline_name}.
      Create about {n_events} events.
      If possible, all periods of time should be equally represented
    '''],
    'fr': ['''
        La réponse doit être au format JSON. Chaque objet représente un événement, avec le format suivant: name, description, startDate, endDate, endDate étant facultative.
        Les dates peuvent être au format YYYY-MM-DD ou YYYY-MM ou YYYY.
        N'écrivez jamais les dates avec BC, AD, CE, BCE, ABY, BBY, etc. S'ils sont négatifs, mettez simplement un signe moins devant l'année.
        Échappez toutes les guillemets doubles avec un backslash.
      ''',
      f'''Générer une chronologie historique de {timeline_name}.
        Créer environ {n_events} événements.
        Si possible, toutes les périodes de temps doivent être également représentées
      '''],
      'it': ['''
        La risposta deve essere in formato JSON. Ogni oggetto rappresenta un evento, con il seguente formato: name, description, startDate, endDate, endDate è facoltativa.
        Le date possono essere nel formato YYYY-MM-DD o YYYY-MM o YYYY.
        Non scrivere mai le date con BC, AD, CE, BCE, ABY, BBY, ecc. Se sono negative, basta mettere un segno meno prima dell'anno.
        Esci da tutti i doppi apici con un backslash.
      ''',
      f'''Genera una cronologia storica di {timeline_name}.
        Crea circa {n_events} eventi.
        Se possibile, tutti i periodi di tempo dovrebbero essere rappresentati in modo uguale
      '''],
      'de': ['''
        Die Antwort muss im JSON-Format sein. Jedes Objekt stellt ein Ereignis dar, mit dem folgenden Format: name, description, startDate, endDate, endDate ist optional.
        Daten können im Format YYYY-MM-DD oder YYYY-MM oder YYYY sein.
        Schreiben Sie die Daten niemals mit BC, AD, CE, BCE, ABY, BBY usw. Wenn sie negativ sind, setzen Sie einfach ein Minuszeichen vor das Jahr.
        Escapen Sie alle doppelten Anführungszeichen mit einem Backslash.
      ''',
      f'''Erstellen Sie eine historische Zeitleiste von {timeline_name}.
        Erstellen Sie etwa {n_events} Ereignisse.
        Wenn möglich, sollten alle Zeiträume gleichmäßig vertreten sein
      '''],
      'es': ['''
        La respuesta debe estar en formato JSON. Cada objeto representa un evento, con el siguiente formato: name, description, startDate, endDate, endDate es opcional.
        Las fechas pueden estar en formato YYYY-MM-DD o YYYY-MM o YYYY.
        Nunca escriba las fechas con BC, AD, CE, BCE, ABY, BBY, etc. Si son negativos, simplemente ponga un signo menos antes del año.
        Escapa todas las comillas dobles con una barra invertida.
      ''',
      f'''Generar una línea de tiempo histórica de {timeline_name}.
        Crea alrededor de {n_events} eventos.
        Si es posible, todos los períodos de tiempo deben estar representados por igual
      '''],
      'pt': ['''
        A resposta deve estar no formato JSON. Cada objeto representa um evento, com o seguinte formato: name, description, startDate, endDate, endDate é opcional.
        As datas podem estar no formato YYYY-MM-DD ou YYYY-MM ou YYYY.
        Nunca escreva as datas com BC, AD, CE, BCE, ABY, BBY, etc. Se forem negativos, basta colocar um sinal de menos antes do ano.
        Escape todas as aspas duplas com uma barra invertida.
      ''',
      f'''Gerar uma linha do tempo histórica de {timeline_name}.
        Crie cerca de {n_events} eventos.
        Se possível, todos os períodos de tempo devem ser representados igualmente
      '''],
  }

def get_quiz_prompts(n_events, events):
    return {
      'en': ['Response has to be in JSON format. Each object represents a question, with the following format: question, options, answer.' ,
       f'''
        Given the events provided at the end of the prompt, generate a historical quiz with {n_events} questions, with multiple choice answers (4 options).
        Be as creative as possible, and make sure the questions are not too easy.
        Questions and answers have to leverage all the information provided in the events, in as much fields as possible (name, description, start date, end date).
        The answer should never be in the question.
        {events}
       '''
        ],
        'fr': ['La réponse doit être au format JSON. Chaque objet représente une question, avec le format suivant: question, options, answer.' ,
        f'''
        Étant donné les événements fournis à la fin de l'invite, générer un quiz historique avec {n_events} questions, avec des réponses à choix multiples (4 options).
        Soyez aussi créatif que possible et assurez-vous que les questions ne sont pas trop faciles.
        Les questions et les réponses doivent exploiter toutes les informations fournies dans les événements, dans autant de champs que possible (nom, description, date de début, date de fin).
        La réponse ne doit jamais être dans la question.
        {events}
        '''
        ],
        'it': ['La risposta deve essere in formato JSON. Ogni oggetto rappresenta una domanda, con il seguente formato: question, options, answer.' ,
        f'''

        Dati gli eventi forniti alla fine dell'invito, genera un quiz storico con {n_events} domande, con risposte a scelta multipla (4 opzioni).
        Sii il più creativo possibile e assicurati che le domande non siano troppo facili.
        Le domande e le risposte devono sfruttare tutte le informazioni fornite negli eventi, in quanti più campi possibile (nome, descrizione, data di inizio, data di fine).
        La risposta non deve mai essere nella domanda.
        {events}
        '''
        ],
        'de': ['Die Antwort muss im JSON-Format sein. Jedes Objekt stellt eine Frage dar, mit dem folgenden Format: question, options, answer.' ,
        f'''
        Angesichts der Ereignisse, die am Ende der Aufforderung angegeben sind, generieren Sie ein historisches Quiz mit {n_events} Fragen mit Mehrfachauswahlantworten (4 Optionen).
        Seien Sie so kreativ wie möglich und stellen Sie sicher, dass die Fragen nicht zu einfach sind.
        Fragen und Antworten müssen alle in den Ereignissen angegebenen Informationen nutzen, in so vielen Feldern wie möglich (Name, Beschreibung, Startdatum, Enddatum).
        Die Antwort sollte niemals in der Frage sein.
        {events}
        '''
        ],
        'es': ['La respuesta debe estar en formato JSON. Cada objeto representa una pregunta, con el siguiente formato: question, options, answer.' ,
        f'''
        Dados los eventos proporcionados al final de la invitación, genere un cuestionario histórico con {n_events} preguntas, con respuestas de opción múltiple (4 opciones).
        Sea lo más creativo posible y asegúrese de que las preguntas no sean demasiado fáciles.
        Las preguntas y respuestas deben aprovechar toda la información proporcionada en los eventos, en la mayor cantidad de campos posible (nombre, descripción, fecha de inicio, fecha de finalización).
        La respuesta nunca debe estar en la pregunta.
        {events}
        '''
        ],
        'pt': ['A resposta deve estar no formato JSON. Cada objeto representa uma pergunta, com o seguinte formato: question, options, answer.' ,
        f'''
        Dados os eventos fornecidos no final do convite, gere um quiz histórico com {n_events} perguntas, com respostas de múltipla escolha (4 opções).
        Seja o mais criativo possível e certifique-se de que as perguntas não sejam muito fáceis.
        As perguntas e respostas devem aproveitar todas as informações fornecidas nos eventos, em quantos campos forem possíveis (nome, descrição, data de início, data de término).
        A resposta nunca deve estar na pergunta.
        {events}
        '''
        ]
    }
