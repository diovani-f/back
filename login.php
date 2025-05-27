<?php
header('Content-Type: application/json');

$host = 'dpg-d0qgcsjipnbc73ebvoeg-a';
$port = '5432';
$db   = 'diovani';
$user = 'diovani';
$pass = 'Ji7huPzuwV9wxDTimf3TgXKrvIhH6e6X';

try {
    $pdo = new PDO("pgsql:host=$host;port=$port;dbname=$db", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Erro ao conectar com banco de dados']);
    exit;
}

$data = json_decode(file_get_contents('php://input'), true);

if (!isset($data['email'], $data['senha'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Email e senha são obrigatórios']);
    exit;
}

$email = $data['email'];
$senha = $data['senha'];

$stmt = $pdo->prepare('SELECT id, nome, senha FROM usuarios WHERE email = :email');
$stmt->execute(['email' => $email]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$user) {
    http_response_code(401);
    echo json_encode(['error' => 'Credenciais inválidas']);
    exit;
}

if (!password_verify($senha, $user['senha'])) {
    http_response_code(401);
    echo json_encode(['error' => 'Credenciais inválidas']);
    exit;
}

// Gera token aleatório simples (32 caracteres hex)
$token = bin2hex(random_bytes(16));

echo json_encode([
    'token' => $token,
    'usuario' => [
        'id' => $user['id'],
        'nome' => $user['nome'],
        'email' => $email
    ]
]);
