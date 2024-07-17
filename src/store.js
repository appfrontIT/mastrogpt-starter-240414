import { writable } from 'svelte/store';

export const logged = writable(false)

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
        url: 'api/my/base/invoke/general',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		})
    },
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
        url: 'api/my/base/invoke/walkiria',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		}),
        editor: {
            'package': '',
            'name': '',
            'function': '',
            'description': '',
            'language': ''
        },
        showEditor: false
    },
    {
        url: 'api/my/base/invoke/admin',
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
        url: 'api/my/html_gen/bot',
        history: new Array(),
        messageFeed: new Array({host: false, name: 'Hari', timestamp: `Today @ ${getCurrentTimestamp()}`, message: `
        Ciao! In questa sezione ti aiuteró a creare un interfaccia
        per visualizzare quello di cui hai bisogno!
        L'interfaccia verrá creata sottoforma di pagina HTML,
        e verrá deployata come parte di una tua azione.
        Utilizza il menu di destra per personalizzare la tua pagina
        e darmi indicazioni su come costruirla!
        Il mio consiglio é quello di essere piú specifico possibile!
        Se ad esempio vuoi visualizzare una tabella,
        dimmi quale azione ritorna la tabella cosí che possa incorporarla
        all'interno della pagina.
        Puoi personalizzare lo stile e il layout, cosí puoi aiutarmi
        a visualizzare i dati nella maniera che preferisci!
        Ti consiglio inoltre di fornirmi una descrizione
        dettagliata della pagina che vuoi creare.
        Una volta che avrai finito di personalizzare tutto,
        inviami tutte le informazioni utilizzando il pulsante 'procedi'!
        `, color: 'variant-soft-primary'}),
        editor: {
            'package': '',
            'name': '',
            'function': '',
            'description': '',
            'language': ''
        },
        showEditor: false
    },
    {
        url: 'api/my/base/invoke/chart',
        history: new Array(),
        messageFeed: new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Benvenuto! Come posso aiutarti oggi?`,
			color: 'variant-soft-primary'
		}),
        editor: {
            'package': '',
            'name': '',
            'function': '',
            'description': '',
            'language': ''
        },
        showEditor: false
    },
])

export const selector = writable(0);

export function set_dark_mode() {
    const e=document.documentElement.classList,t=localStorage.getItem("modeUserPrefers")==="false",n=!("modeUserPrefers"in localStorage),r=window.matchMedia("(prefers-color-scheme: dark)").matches;
    t||n&&r?e.add("dark"):e.remove("dark")
}

export const templates = writable([
    {
        "name": "Band",
        "img": "https://www.w3schools.com/w3css/img_temp_band.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_band.htm",
    },
    {
        "name": "Blog",
        "img": "https://www.w3schools.com/w3css/img_temp_blog.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_blog.htm",
    },
    {
        "name": "Gourmet Catering",
        "img": "https://www.w3schools.com/w3css/img_temp_gourmet_catering.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_gourmet_catering.htm",
    },
    {
        "name": "Food Blog",
        "img": "https://www.w3schools.com/w3css/img_temp_food_blog.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_food_blog.htm",
    },
    {
        "name": "Fashion blog",
        "img": "https://www.w3schools.com/w3css/img_temp_fashion_blog.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_fashion_blog.htm",
    },
    {
        "name": "CV",
        "img": "https://www.w3schools.com/w3css/img_temp_cv.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_cv.htm",
    },
    {
        "name": "Comingsoon",
        "img": "https://www.w3schools.com/w3css/img_temp_comingsoon.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_coming_soon.htm",
    },
    {
        "name": "Photo",
        "img": "https://www.w3schools.com/w3css/img_temp_photo.JPG",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_photo.htm",
    },
    {
        "name": "Interior Design",
        "img": "https://www.w3schools.com/w3css/img_temp_interior_design.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_interior_design.htm",
    },
    {
        "name": "Startup",
        "img": "https://www.w3schools.com/w3css/img_temp_startup.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_startup.htm",
    },
    {
        "name": "App Launch",
        "img": "https://www.w3schools.com/w3css/img_temp_app_launch.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_app_launch.htm",
    },
    {
        "name": "Marketing",
        "img": "https://www.w3schools.com/w3css/img_temp_marketing.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_marketing.htm",
    },
    {
        "name": "Website",
        "img": "https://www.w3schools.com/w3css/img_temp_website.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_website.htm",
    },
    {
        "name": "Art",
        "img": "https://www.w3schools.com/w3css/img_temp_art.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_streetart.htm",
    },
    {
        "name": "Webpage",
        "img": "https://www.w3schools.com/w3css/img_temp_webpage.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_webpage.htm",
    },
    {
        "name": "Social",
        "img": "https://www.w3schools.com/w3css/img_temp_social.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_social.htm",
    },
    {
        "name": "Analytics",
        "img": "https://www.w3schools.com/w3css/img_temp_analytics.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_analytics.htm",
    },
    {
        "name": "Apartment Rental",
        "img": "https://www.w3schools.com/w3css/img_temp_apartment_rental.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_apartment_rental.htm",
    },
    {
        "name": "Hotel",
        "img": "https://www.w3schools.com/w3css/img_temp_hotel.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_hotel.htm",
    },
    {
        "name": "Travel",
        "img": "https://www.w3schools.com/w3css/img_temp_travel2.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_travel2.htm",
    },
    {
        "name": "50/50",
        "img": "https://www.w3schools.com/w3css/img_temp_fifty.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_fifty.htm",
    },
    {
        "name": "Mail",
        "img": "https://www.w3schools.com/w3css/img_temp_mail.jpg",
        "demo": "https://www.w3schools.com/w3css/tryw3css_templates_mail.htm",
    },
])

export const edges = writable([]);
export const nodes = writable([]);
export const status = writable([
    200, 201, 204, 400, 401, 403, 404, 500
]);

export const tabSet = writable(0);
export const activation_name = writable(null);