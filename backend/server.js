'use strict';

const express = require('express');
const {
    createHash,
} = require('node:crypto');

// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

// App
const app = express();
app.use(express.json());
// custom error handler
app.use((err, req, res, next) => {
    console.error(err.stack)
    res.status(500).send()
})
app.disable('x-powered-by');
app.post('/md5', (req, res, next) => {
    res.json({"hash": createHash('md5').update(req.body.data).digest('hex')});
});
// custom 404
app.use((req, res, next) => {
    res.status(404).send()
})

app.listen(PORT, HOST, () => {
    console.log(`Running on http://${HOST}:${PORT}`);
});
