import { error } from '@sveltejs/kit';
import dotenv from 'dotenv';
import { MongoClient } from 'mongodb';
import { mongo_client } from '$lib/server/mongo'

/** @type {import('./$types').RequestHandler} */
export async function GET({ url, cookies }) {

	const sessionid = cookies.get('appfront-sess-cookie');
    // const uri = process.env['CONNECTION_STRING'];
    // if (!uri) {
	// 	return new Response(null, {headers: {}, status: 500})
	// }
	// const client = new MongoClient(uri);
	if (!mongo_client) {
		return new Response(null, {headers: {}, status: 500});
	}
	
	const db = mongo_client.db('mastrogpt');
	const collection = db.collection('users');
	let user = await collection.findOne({'cookie': sessionid});
	let stream = null;
	if (user) {
		if ('chat' in user) {
			const chat = user['chat']
			stream = new ReadableStream({
				async start(controller) {
					controller.enqueue(`data: ${JSON.stringify(chat)}\n\n`)
					controller.close()
					await collection.updateOne({'cookie': sessionid},  {"$unset": {"chat": 1}})
				},
				cancel() {
				}
			});
		}
	}

    return new Response(stream, {
        headers: {
            // Denotes the response as SSE
            'Content-Type': 'text/event-stream', 
            // Optional. Request the GET request not to be cached.
            'Cache-Control': 'no-cache', 
        }
    })
}