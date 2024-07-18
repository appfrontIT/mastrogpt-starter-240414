import { json } from '@sveltejs/kit'
import type { RequestHandler } from './$types'

import { exec } from 'node:child_process'

export const POST:RequestHandler  = async ({request,locals}) => {

    exec('ls ./', (err, stdout,stderr) => {
        console.log({stdout})
    })

    return json({message:"called ls"})
}