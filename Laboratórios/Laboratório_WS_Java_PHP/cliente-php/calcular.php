<?php
// Captura os dados do formulário
$num1 = $_GET['num1'] ?? 0;
$num2 = $_GET['num2'] ?? 0;
$operacao = $_GET['operacao'] ?? 'somar';

// Monta a URL da API Java (Ex: http://localhost:8080/somar/10/5)
$url = "http://localhost:8080/$operacao/$num1/$num2";

// Inicializa o cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Executa a requisição
$resposta = curl_exec($ch);

// Verifica erros de conexão
if (curl_errno($ch)) {
    die("Erro na requisição: " . curl_error($ch));
}

curl_close($ch);

// Redireciona para a página de resultado enviando a resposta na URL
header("Location: resultado.php?resposta=" . urlencode($resposta));
?>