import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpRequest.BodyPublishers;

public class ClientJava {
    public static void main(String[] args) {
        HttpClient client = HttpClient.newHttpClient();
        String json = "{\"tipo\":\"Empresa\",\"nome_plano\":\"Plano Java\",\"preco_base\":500.0,\"is_ativo\":true,\"cnpj\":\"00.000/0001-00\"}";

        // Exemplo POST
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/planos"))
                .header("Content-Type", "application/json")
                .POST(BodyPublishers.ofString(json))
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("Resposta do Servidor: " + response.body());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}