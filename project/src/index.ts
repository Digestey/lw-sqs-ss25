import { MainClient } from 'pokenode-ts';
import express from 'express';

const app = express();
const PORT = 3000;
const api = new MainClient();
const MAX_POKEMON = 1025;

app.get("/", async (req, res) => {
  var pokemon:string = "";
  const pokemon_id:number = Math.round(Math.random() * MAX_POKEMON);
  await api.pokemon
  .getPokemonById(pokemon_id)
  .then((data) => pokemon = data.name) // will output "Luxray"
  .catch((error) => console.error(error));
  res.send("My favourite pokemon is "+pokemon);
});

app.listen(PORT);
