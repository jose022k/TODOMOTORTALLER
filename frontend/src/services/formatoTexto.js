/**
 * Utilidades de formato de texto compartidas.
 */

/**
 * Capitaliza la primera letra de cada palabra respetando los acentos.
 *   "josé maría"  → "José María"
 *   "maría josé"  → "María José"
 *
 * Se usa una regex Unicode en lugar de \b porque en JavaScript el acento
 * cuenta como límite de palabra y convertía "josé" en "JosÉ".
 */
export function capitalizarNombre(valor) {
  if (!valor) return "";
  return valor.replace(/(^|\s)(\p{L})/gu, (_, separador, letra) =>
    separador + letra.toLocaleUpperCase("es")
  );
}
