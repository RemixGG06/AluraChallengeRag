# Manual de Red Corporativa — Departamento de Operaciones

## 1. Conexión a la VPN

Para conectarte a la VPN corporativa sigue estos pasos:

1. Instala el cliente **GlobalProtect** desde el portal de software interno.
2. Abre el cliente e ingresa el portal: `vpn.empresa.com`.
3. Usa tus credenciales de Active Directory (el mismo usuario y contraseña del
   correo corporativo).
4. Si la conexión falla con error de autenticación, verifica que tu contraseña
   no esté vencida y reinicia el servicio `PanGPS` en tu equipo.
5. Si el problema persiste más de 15 minutos, escala al NOC (extensión 4321).

## 2. WiFi corporativo

- Red **EMPRESA-CORP**: solo para equipos de dominio. Se conecta
  automáticamente con certificado.
- Red **EMPRESA-GUEST**: para visitas y dispositivos personales. La contraseña
  se rota **cada lunes a las 08:00** y se publica en la cartelera digital del
  piso 2 y en el canal #ti-anuncios de Slack.

## 3. VLANs de la red

| VLAN | Uso | Segmento |
|------|-----|----------|
| 10 | Usuarios corporativos | 10.10.10.0/24 |
| 20 | Servidores de producción | 10.10.20.0/24 |
| 30 | Invitados | 10.10.30.0/24 |
| 40 | Voz IP | 10.10.40.0/24 |

## 4. Impresoras de red

Las impresoras siguen la nomenclatura `IMP-PISO-NUMERO`. Ejemplo:
`IMP-P3-02` es la impresora 2 del piso 3. Se instalan desde
`\\printsrv\impresoras` con doble clic.
