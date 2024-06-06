import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({fetch}) {
    const res = await fetch('api/my/base/auth/user', {
        method: 'GET',
        credentials: 'include'
    })
    const user = await res.json();
    const response = await fetch('api/my/db/get_crawled_pages', {
        method: "GET",
        headers: {"Authorization": "Bearer " + user['JWT']},
    })
    if (response.ok) {
        const obj = await response.json();
        console.log(obj);
        return {'data': obj, 'user': user};
    }
    
    error(404, 'Not found');
}