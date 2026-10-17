import { ref } from 'vue'

// Mismo patrón que AllSafe: el tema elegido se guarda en localStorage y se
// aplica como data-theme en <html>. Sin elección previa, sigue al sistema.
function leerTema() {
  try {
    return localStorage.getItem('theme')
  } catch {
    return null
  }
}

const guardado = leerTema()
const isDark = ref(
  guardado ? guardado === 'dark' : window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false,
)

function aplicar(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

aplicar(isDark.value)

export function useTheme() {
  function toggle() {
    isDark.value = !isDark.value
    aplicar(isDark.value)
    try {
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    } catch {
      // Sin almacenamiento disponible el tema solo dura la sesión
    }
  }
  return { isDark, toggle }
}
