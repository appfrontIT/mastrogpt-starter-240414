import { writable } from 'svelte/store';

export const user = writable(null)
export const JWT = writable(null)
export const walkiria_role = writable(`
Act as a software Architect. You're specialized in working with OpenWhisk and Nuvolaris platform.
You will work as a bridge between the user and the platform. To do so, you must be collect informations about your client request.

Whenever the user ask a question, think if it's the case to ask for more informations. You are very meticolous in your job.
Use all the information collected to generate an answer. You can show examples as well when collection informations. Example: 'assistan': 'are you thinking about something like this: <example>'.

You must display any link with the full path, without alias. Open links in an external tab, always!

If you're not totally sure which function to call, you can ask the user to clear your doubts. Example:
{
    "user": "how do you use get_next_line action?"
    "assistant": "are you looking for some information and use cases about get_next_line?"
    "user": "yes exactly!"
    "assistant": "<call internal function action_info>"
}

Take your time to answer and try to think backward. Don't forget to lookup the chat history to understand what the user wants.
You can't be lazy, NEVER! The user needs your help!
`);

export function getCurrentTimestamp() {
    const date = new Date().toLocaleString('en-GB', { hour: 'numeric', minute: 'numeric', hour12: true });
    return date;
}

export let editor = writable({
    'package': '',
    'name': '',
    'function': '',
    'description': '',
    'language': ''
});

export const chat_room = writable([
    {
        url: 'api/my/base/invoke/lookinglass',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		})
    },
    {
        url: '/api/my/base/invoke/walkiria',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		})
    },
    {
        url: '/api/my/base/invoke/admin',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		})
    },
    {
        url: '/api/my/html_gen/bot',
        history: new Array(),
        messageFeed: new Array({host: false, name: 'Hari', timestamp: `Today @ ${getCurrentTimestamp()}`, message: `
        Ciao! In questa sezione ti aiuteró a creare un interfaccia per visualizzare quello di cui hai bisogno!
        L'interfaccia verrá creata sottoforma di pagina HTML, e verrá deployata come parte di una tua azione.
        Utilizza il menu di destra per personalizzare la tua pagina e darmi indicazioni su come costruirla!
        Il mio consiglio é quello di essere piú specifico possibile! Se ad esempio vuoi visualizzare una tabella,
        dimmi quale azione ritorna la tabella cosí che possa incorporarla all'interno della pagina.
        Puoi personalizzare lo stile e il layout, cosí puoi aiutarmi a visualizzare i dati nella maniera che preferisci!
        Ti consiglio inoltre di fornirmi una descrizione dettagliata della pagina che vuoi creare.
        Una volta che avrai finito di personalizzare tutto, inviami tutte le informazioni utilizzando il pulsante 'procedi'!
        `, color: 'variant-soft-primary'})
    },
    {
        url: '/api/my/base/invoke/chart',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		})
    },
])

export const selector = writable(-1);