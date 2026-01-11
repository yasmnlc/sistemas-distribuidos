const axios = require('axios');

const API_URL = 'http://localhost:8000/planos';

async function main() {
    try {
        // 1. Adicionar Plano
        console.log("--- Adicionando Plano ---");
        const novoPlano = {
            tipo: "Individual",
            nome_plano: "Plano JS Client",
            preco_base: 200.0,
            is_ativo: true,
            cpf_titular: "123.456.789-00"
        };
        const resPost = await axios.post(API_URL, novoPlano);
        console.log("Plano Criado:", resPost.data);
        const id = resPost.data.codigo;

        // 2. Listar
        console.log("\n--- Listando Planos ---");
        const resList = await axios.get(API_URL);
        console.log(resList.data);

        // 3. Remover
        console.log(`\n--- Removendo Plano ${id} ---`);
        await axios.delete(`${API_URL}/${id}`);
        console.log("Removido com sucesso.");

    } catch (error) {
        console.error("Erro:", error.message);
    }
}

main();