/**
 * Reglas de validación del registro de clientes (compartidas entre
 * ClienteRegisterView y LoginView para que siempre digan lo mismo).
 *
 * Reglas:
 *  - nombre   → mínimo dos palabras (nombre y apellido)
 *  - cedula   → solo números, entre 6 y 8 dígitos, y sin patrones falsos
 *               (consecutivos 12345678 / 87654321 o todos iguales 11111111)
 *  - telefono → solo números, exactamente 11 dígitos (04121234567)
 *  - email    → solo gmail / outlook / icloud
 *  - direccion → obligatoria
 *
 * Devuelve "" cuando el valor es válido o el mensaje de error cuando no.
 */

/**
 * Detecta cédulas que parecen inventadas:
 *  - todos los dígitos iguales: 11111111, 22222222, 33333333…
 *  - consecutivos ascendentes:  12345678
 *  - consecutivos descendentes: 87654321
 * Solo se evalúa a partir de 6 dígitos (la longitud mínima de una cédula),
 * para no molestar mientras se escribe.
 */
function esPatronFalsoCedula(v) {
  if (v.length < 6) return false;
  if (/^(\d)\1+$/.test(v)) return true;
  let ascendente = true;
  let descendente = true;
  for (let i = 1; i < v.length; i++) {
    const anterior = v.charCodeAt(i - 1) - 48;
    const actual = v.charCodeAt(i) - 48;
    if (actual !== anterior + 1) ascendente = false;
    if (actual !== anterior - 1) descendente = false;
  }
  return ascendente || descendente;
}

export function validarCampoRegistro(campo, valor) {
  const v = (valor || "").trim();

  if (campo === "nombre") {
    if (!v) return "El nombre y apellido es obligatorio";
    if (v.split(/\s+/).length < 2) return "Debes agregar tu apellido (nombre y apellido)";
    return "";
  }

  if (campo === "cedula") {
    if (!v) return "La cédula es obligatoria";
    if (!/^\d+$/.test(v)) return "La cédula debe contener solo números";
    if (v.length < 6 || v.length > 8) return "La cédula debe tener entre 6 y 8 dígitos";
    if (esPatronFalsoCedula(v)) return "No estás introduciendo un número de cédula real";
    return "";
  }

  if (campo === "telefono") {
    if (!v) return "El teléfono es obligatorio";
    if (!/^\d+$/.test(v)) return "El teléfono debe contener solo números";
    if (v.length !== 11) return "El teléfono debe tener exactamente 11 dígitos (ej: 04121234567)";
    return "";
  }

  if (campo === "email") {
    if (!v) return "El correo es obligatorio";
    if (!/^[^\s@]+@(gmail\.com|outlook\.com|icloud\.com)$/i.test(v)) {
      return "El correo debe terminar en @gmail.com, @outlook.com o @icloud.com";
    }
    return "";
  }

  if (campo === "direccion") {
    if (!v) return "La dirección es obligatoria";
    return "";
  }

  return "";
}

/** Campos que se verifican contra el servidor con /auth/disponibilidad */
export const CAMPOS_DISPONIBLES = ["email", "cedula", "telefono"];

/** ¿El mensaje corresponde a un dato ya registrado? */
export function esErrorDuplicado(msg) {
  return typeof msg === "string" && /ya está (registrado|registrada)/.test(msg);
}
