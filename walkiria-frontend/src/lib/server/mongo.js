import { MongoClient } from 'mongodb';
import { onMount } from 'svelte';

/** @type {MongoClient | undefined} */
export let mongo_client = get_clint();

function get_clint() {
    const uri = process.env['CONNECTION_STRING'];
    if (!uri) {
        return undefined
    }
    const client = new MongoClient(uri);
    return client;
}