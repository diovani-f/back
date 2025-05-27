<?php
header('Content-Type: application/json');

// Configurações do banco (Render)
$host = "dpg-d0qgcsjipnbc73ebvoeg-a.render.com";
$port = "5432";
$dbname = "jardimdb";
$user = "diovani";
$password = "Ji7huPzuwV9wxDTimf3TgXKrvIhH6e6X";

// Função para enviar resposta JSON e sair
function send_response($status_code, $data) {
    http_response_code($status_code);
    echo json_encode($data);
    exit;
}

// Conectar no banco usando PDO
try {
    $dsn = "pgsql:host=$host;port=$port;dbname=$dbname";
    $pdo = new PDO($dsn, $user, $password, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
} catch (PDOException $e) {
    send_response(500, ["error" => "Erro ao conectar no banco de dados."]);
}

// Roteamento básico - só aceita POST /usuarios
$method = $_SERVER['REQUEST_METHOD'];
$uri = $_SERVER['REQUEST_URI'];

if ($method === 'POST' && preg_match('#^/usuarios/?$#', $uri)) {
    // Lê JSON enviado no corpo da requisição
    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input) {
        send_response(400, ["error" => "JSON inválido."]);
    }

    // Validação básica
    $nome = trim($input['nome'] ?? '');
    $email = trim($input['email'] ?? '');
    $senha = $input['senha'] ?? '';

    if (!$nome || !$email || !$senha) {
        send_response(400, ["error" => "Campos 'nome', 'email' e 'senha' são obrigatórios."]);
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        send_response(400, ["error" => "Email inválido."]);
    }

    // Hash da senha
    $senhaHash = password_hash($senha, PASSWORD_DEFAULT);

    // Tenta inserir no banco
    try {
        $sql = "INSERT INTO usuarios (nome, email, senha) VALUES (:nome, :email, :senha)";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            ':nome' => $nome,
            ':email' => $email,
            ':senha' => $senhaHash
        ]);
        send_response(201, ["message" => "Usuário cadastrado com sucesso."]);
    } catch (PDOException $e) {
        // Checa se email já existe (violação de UNIQUE)
        if ($e->getCode() == '23505') {
            send_response(409, ["error" => "Email já cadastrado."]);
        } else {
            send_response(500, ["error" => "Erro no banco de dados."]);
        }
    }
} else {
    send_response(404, ["error" => "Rota não encontrada."]);
}
