    import { error } from '@sveltejs/kit';
    
    /** @type {import('./$types').PageLoad} */
    export async function load({fetch}) {
        const res = await fetch('api/my/base/auth/user', {
            method: 'GET',
            credentials: 'include'
        })
        if (!res.ok) {
            throw error(404)
        }
        const user = await res.json();
        const response = await fetch('api/my/db/minio/static/find_all', {
            method: "GET",
            headers: {"Authorization": "Bearer " + user['JWT']},
        })
        if (response.ok) {
            const obj = await response.json();
            return {'data': obj, 'user': user};
        }
        throw error(404)

    }