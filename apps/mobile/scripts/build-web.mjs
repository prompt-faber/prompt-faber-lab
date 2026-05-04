import { mkdir, writeFile } from "node:fs/promises";

await mkdir(new URL("../www/", import.meta.url), { recursive: true });
await writeFile(
  new URL("../www/index.html", import.meta.url),
  `<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Prompt Faber Lab</title>
  </head>
  <body>
    <noscript>Habilite JavaScript para executar o Prompt Faber Lab.</noscript>
    <div id="root">Prompt Faber Lab</div>
  </body>
</html>
`,
  "utf-8"
);
