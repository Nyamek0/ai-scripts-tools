export type Lang = "fr" | "en";

const fr: Record<string, string> = {
  // ── Navbar ──────────────────────────────────────────────────────────────────
  "nav.tools":   "Outils",
  "nav.my_jobs": "Mes traitements",
  "nav.login":   "Connexion",
  "nav.register":"S'inscrire",
  "nav.logout":  "Se déconnecter",

  // ── Page d'accueil ──────────────────────────────────────────────────────────
  "home.badge":       "Open-source · 100% gratuit · 100% local",
  "home.h1_a":        "Des outils IA.",
  "home.h1_b":        "Gratuits.",
  "home.h1_c":        "Puissants.",
  "home.desc":        "Suppression de fond, transcription, OCR, synthèse vocale et plus encore — sans abonnement, sans données envoyées dans le cloud.",
  "home.cta":         "Découvrir les outils",
  "home.tools_title": "{n} outils disponibles",
  "home.tools_sub":   "Chaque outil fonctionne de façon indépendante, sans configuration.",

  // ── Footer ──────────────────────────────────────────────────────────────────
  "footer.desc":     "Plateforme d'outils IA open-source — 100% gratuit, 100% local.",
  "footer.tools":    "Outils",
  "footer.register": "S'inscrire",

  // ── Dashboard ───────────────────────────────────────────────────────────────
  "dash.title":        "Mes traitements",
  "dash.total_1":      "traitement au total",
  "dash.total_n":      "traitements au total",
  "dash.new_tool":     "Nouvel outil",
  "dash.search":       "Rechercher par module…",
  "dash.all_statuses": "Tous les statuts",
  "dash.col_module":   "Module",
  "dash.col_file":     "Fichier",
  "dash.col_status":   "Statut",
  "dash.col_duration": "Durée",
  "dash.col_date":     "Date",
  "dash.col_action":   "Action",
  "dash.download":     "Télécharger",
  "dash.empty":        "Aucun traitement pour l'instant.",
  "dash.try_tool":     "Essayer un outil",
  "dash.prev":         "Précédent",
  "dash.next":         "Suivant",
  "dash.page":         "Page {p} / {total}",

  // ── Statuts ─────────────────────────────────────────────────────────────────
  "status.success":    "Terminé",
  "status.failed":     "Échoué",
  "status.processing": "En cours",
  "status.pending":    "En attente",

  // ── Auth ────────────────────────────────────────────────────────────────────
  "auth.login_title":    "Bon retour 👋",
  "auth.login_sub":      "Connectez-vous pour accéder à vos outils",
  "auth.register_title": "Créer un compte",
  "auth.register_sub":   "Rejoignez la plateforme gratuite",
  "auth.full_name":      "Nom complet",
  "auth.optional":       "(optionnel)",
  "auth.email":          "Email",
  "auth.password":       "Mot de passe",
  "auth.pwd_hint_reg":   "Min. 8 caractères avec chiffres",
  "auth.pwd_hint_login": "••••••••",
  "auth.remember":       "Se souvenir de moi",
  "auth.btn_login":      "Se connecter",
  "auth.btn_register":   "Créer mon compte",
  "auth.no_account":     "Pas encore de compte ?",
  "auth.has_account":    "Déjà un compte ?",
  "auth.link_register":  "S'inscrire",
  "auth.link_login":     "Se connecter",
  "auth.error":          "Une erreur est survenue",

  // ── Page outil ──────────────────────────────────────────────────────────────
  "tool.not_found":   "Outil introuvable",
  "tool.back_home":   "Retour à l'accueil",
  "tool.back_all":    "Tous les outils",
  "tool.label_text":  "Votre texte",
  "tool.label_pdfs":  "Vos fichiers PDF",
  "tool.label_file":  "Votre fichier",
  "tool.processing":  "Traitement en cours…",
  "tool.process":     "Traiter",
  "tool.new":         "Nouveau traitement",
  "tool.err_text":    "Veuillez saisir un texte",
  "tool.err_file":    "Veuillez sélectionner un fichier",
  "tool.err_generic": "Une erreur est survenue",
  "tool.done":        "Traitement terminé",
  "tool.img":         "image",
  "tool.audio":       "fichier audio",
  "tool.video":       "vidéo",
  "tool.drop_pdf":    "Déposez vos fichiers PDF (2–20 fichiers)",
  "tool.tts_ph":      "Saisissez le texte à convertir en audio…",
  "tool.sum_ph":      "Collez ou tapez votre texte à résumer…",

  // ── Upload ──────────────────────────────────────────────────────────────────
  "upload.browse":  "ou cliquez pour parcourir · max {n} MB",
  "upload.too_big": "Fichier trop volumineux (max {n} MB)",

  // ── Résultat ────────────────────────────────────────────────────────────────
  "result.done":         "Traitement terminé !",
  "result.processed_in": "Traité en",
  "result.download":     "Télécharger le résultat",

  // ── Saisie texte ────────────────────────────────────────────────────────────
  "text.remaining":   "caractères restants",
  "text.remaining_1": "caractère restant",

  // ── Noms & descriptions des modules ─────────────────────────────────────────
  "module.bg-remove.name":      "Suppression de fond",
  "module.bg-remove.desc":      "Supprime l'arrière-plan d'une image en un clic grâce à l'IA.",
  "module.transcribe.name":     "Transcription audio",
  "module.transcribe.desc":     "Convertit un fichier audio en texte (Whisper, 100% local).",
  "module.ocr.name":            "OCR — Image vers texte",
  "module.ocr.desc":            "Extrait le texte d'une image ou d'un screenshot (multi-langues).",
  "module.pdf-merge.name":      "Fusion PDF",
  "module.pdf-merge.desc":      "Fusionne plusieurs fichiers PDF en un seul document.",
  "module.tts.name":            "Synthèse vocale",
  "module.tts.desc":            "Convertit du texte en parole naturelle (12 voix, multi-langues).",
  "module.compress-video.name": "Compression vidéo",
  "module.compress-video.desc": "Réduit le poids d'une vidéo sans perte de qualité visible.",
  "module.summarize.name":      "Résumé de texte",
  "module.summarize.desc":      "Résume automatiquement un texte long en quelques phrases clés.",
  "module.convert-image.name":  "Conversion d'image",
  "module.convert-image.desc":  "Convertit une image dans un autre format (JPEG, PNG, WebP, etc.).",
};

const en: Record<string, string> = {
  // ── Navbar ──────────────────────────────────────────────────────────────────
  "nav.tools":   "Tools",
  "nav.my_jobs": "My jobs",
  "nav.login":   "Log in",
  "nav.register":"Sign up",
  "nav.logout":  "Log out",

  // ── Home ────────────────────────────────────────────────────────────────────
  "home.badge":       "Open-source · 100% free · 100% local",
  "home.h1_a":        "AI Tools.",
  "home.h1_b":        "Free.",
  "home.h1_c":        "Powerful.",
  "home.desc":        "Background removal, transcription, OCR, text-to-speech and more — no subscription, no data sent to the cloud.",
  "home.cta":         "Explore tools",
  "home.tools_title": "{n} tools available",
  "home.tools_sub":   "Each tool works independently, no setup required.",

  // ── Footer ──────────────────────────────────────────────────────────────────
  "footer.desc":     "Open-source AI tools platform — 100% free, 100% local.",
  "footer.tools":    "Tools",
  "footer.register": "Sign up",

  // ── Dashboard ───────────────────────────────────────────────────────────────
  "dash.title":        "My jobs",
  "dash.total_1":      "job total",
  "dash.total_n":      "jobs total",
  "dash.new_tool":     "New tool",
  "dash.search":       "Search by module…",
  "dash.all_statuses": "All statuses",
  "dash.col_module":   "Module",
  "dash.col_file":     "File",
  "dash.col_status":   "Status",
  "dash.col_duration": "Duration",
  "dash.col_date":     "Date",
  "dash.col_action":   "Action",
  "dash.download":     "Download",
  "dash.empty":        "No jobs yet.",
  "dash.try_tool":     "Try a tool",
  "dash.prev":         "Previous",
  "dash.next":         "Next",
  "dash.page":         "Page {p} / {total}",

  // ── Statuts ─────────────────────────────────────────────────────────────────
  "status.success":    "Done",
  "status.failed":     "Failed",
  "status.processing": "Processing",
  "status.pending":    "Pending",

  // ── Auth ────────────────────────────────────────────────────────────────────
  "auth.login_title":    "Welcome back 👋",
  "auth.login_sub":      "Log in to access your tools",
  "auth.register_title": "Create an account",
  "auth.register_sub":   "Join the free platform",
  "auth.full_name":      "Full name",
  "auth.optional":       "(optional)",
  "auth.email":          "Email",
  "auth.password":       "Password",
  "auth.pwd_hint_reg":   "Min. 8 characters with digits",
  "auth.pwd_hint_login": "••••••••",
  "auth.remember":       "Remember me",
  "auth.btn_login":      "Log in",
  "auth.btn_register":   "Create account",
  "auth.no_account":     "Don't have an account?",
  "auth.has_account":    "Already have an account?",
  "auth.link_register":  "Sign up",
  "auth.link_login":     "Log in",
  "auth.error":          "An error occurred",

  // ── Tool page ───────────────────────────────────────────────────────────────
  "tool.not_found":   "Tool not found",
  "tool.back_home":   "Back to home",
  "tool.back_all":    "All tools",
  "tool.label_text":  "Your text",
  "tool.label_pdfs":  "Your PDF files",
  "tool.label_file":  "Your file",
  "tool.processing":  "Processing…",
  "tool.process":     "Process",
  "tool.new":         "New processing",
  "tool.err_text":    "Please enter some text",
  "tool.err_file":    "Please select a file",
  "tool.err_generic": "An error occurred",
  "tool.done":        "Processing complete",
  "tool.img":         "image",
  "tool.audio":       "audio file",
  "tool.video":       "video",
  "tool.drop_pdf":    "Drop your PDF files (2–20 files)",
  "tool.tts_ph":      "Enter the text to convert to audio…",
  "tool.sum_ph":      "Paste or type your text to summarize…",

  // ── Upload ──────────────────────────────────────────────────────────────────
  "upload.browse":  "or click to browse · max {n} MB",
  "upload.too_big": "File too large (max {n} MB)",

  // ── Result ──────────────────────────────────────────────────────────────────
  "result.done":         "Processing complete!",
  "result.processed_in": "Processed in",
  "result.download":     "Download result",

  // ── Text input ──────────────────────────────────────────────────────────────
  "text.remaining":   "characters remaining",
  "text.remaining_1": "character remaining",

  // ── Module names & descriptions ─────────────────────────────────────────────
  "module.bg-remove.name":      "Background Removal",
  "module.bg-remove.desc":      "Remove the background from an image in one click using AI.",
  "module.transcribe.name":     "Audio Transcription",
  "module.transcribe.desc":     "Convert an audio file to text (Whisper, 100% local).",
  "module.ocr.name":            "OCR — Image to Text",
  "module.ocr.desc":            "Extract text from an image or screenshot (multi-language).",
  "module.pdf-merge.name":      "PDF Merge",
  "module.pdf-merge.desc":      "Merge multiple PDF files into a single document.",
  "module.tts.name":            "Text to Speech",
  "module.tts.desc":            "Convert text to natural-sounding speech (12 voices, multi-language).",
  "module.compress-video.name": "Video Compression",
  "module.compress-video.desc": "Reduce video file size without noticeable quality loss.",
  "module.summarize.name":      "Text Summary",
  "module.summarize.desc":      "Automatically summarize a long text into a few key sentences.",
  "module.convert-image.name":  "Image Conversion",
  "module.convert-image.desc":  "Convert an image to another format (JPEG, PNG, WebP, etc.).",
};

const translations: Record<Lang, Record<string, string>> = { fr, en };

/** Traduit une clé. Supporte les variables {key}. */
export function t(
  lang: Lang,
  key: string,
  vars?: Record<string, string | number>,
): string {
  let str = translations[lang]?.[key] ?? translations.fr[key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      str = str.replaceAll(`{${k}}`, String(v));
    }
  }
  return str;
}
