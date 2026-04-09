"use client";

import { useState } from "react";

function WaitlistForm({ dark = false }: { dark?: boolean }) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name }),
      });
      if (res.ok) {
        setSubmitted(true);
      } else {
        const data = await res.json();
        setError(data.error || "Er ging iets mis. Probeer het opnieuw.");
      }
    } catch {
      setError("Er ging iets mis. Probeer het opnieuw.");
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="rounded-2xl p-8 text-center border border-emerald-400/30 bg-emerald-950/40">
        <div className="w-14 h-14 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Je staat op de lijst!</h3>
        <p className="text-slate-400">We nemen snel contact op. Jij gaat het halen.</p>
      </div>
    );
  }

  const inputClass = dark
    ? "w-full px-5 py-4 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-violet-400 focus:bg-white/8 text-base transition-colors"
    : "w-full px-5 py-4 rounded-xl bg-white border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 text-base transition-colors";

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 w-full max-w-md mx-auto">
      <input
        type="text"
        placeholder="Je voornaam"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        className={inputClass}
      />
      <input
        type="email"
        placeholder="Je e-mailadres"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        className={inputClass}
      />
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-violet-600 hover:bg-violet-500 disabled:bg-violet-800 disabled:cursor-not-allowed text-white font-semibold py-4 px-8 rounded-xl text-base transition-all cursor-pointer shadow-lg shadow-violet-900/40 hover:shadow-violet-700/40"
      >
        {loading ? "Bezig..." : "Reserveer mijn plek →"}
      </button>
      <p className="text-xs text-slate-500 text-center">
        Gratis aanmelden · Geen spam · Opzeggen wanneer je wilt
      </p>
    </form>
  );
}

const testimonials = [
  {
    quote: "Ik had al opgegeven voor wiskunde. Na acht weken begreep ik eindelijk hoe het werkte — en haalde een 7,8 op mijn eindexamen.",
    name: "Sanne",
    school: "Havo 5 · Amsterdam",
    initials: "S",
    color: "bg-violet-500",
  },
  {
    quote: "Mijn tutor was student aan de TU Delft. Hij snapte precies waar ik vastliep en legde het uit op een manier die bij mij paste.",
    name: "Tim",
    school: "VWO 6 · Utrecht",
    initials: "T",
    color: "bg-indigo-500",
  },
  {
    quote: "Eindelijk iemand die niet gewoon het boek herhaalt. We oefenden échte examenopgaven en ik voelde me echt voorbereid.",
    name: "Fatima",
    school: "Havo 5 · Rotterdam",
    initials: "F",
    color: "bg-fuchsia-500",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#080B14] text-white">

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#080B14]/80 backdrop-blur-md border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-black tracking-tight">
            Slaag<span className="text-violet-400">Zeker</span>
          </span>
          <div className="flex items-center gap-6">
            <a href="#hoe" className="text-sm text-slate-400 hover:text-white transition-colors hidden sm:block">Hoe het werkt</a>
            <a href="#vakken" className="text-sm text-slate-400 hover:text-white transition-colors hidden sm:block">Vakken</a>
            <a
              href="#wachtlijst"
              className="bg-violet-600 hover:bg-violet-500 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-colors"
            >
              Aanmelden
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-36 pb-28 px-6 overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-violet-600/10 rounded-full blur-3xl" />
          <div className="absolute top-20 left-1/4 w-[400px] h-[400px] bg-indigo-600/8 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 text-violet-300 text-sm font-medium px-4 py-2 rounded-full mb-8">
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            Eindexamen 2026 — beperkt aantal plekken
          </div>

          <h1 className="text-5xl sm:text-7xl font-black leading-[1.05] tracking-tight mb-7">
            Jij gaat dit{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
              halen.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed">
            SlaagZeker koppelt jou aan een persoonlijke tutor die precies weet hoe jij leert.
            Geen groepslessen, geen standaard schema's. Alleen jij, jouw tutor, en een plan dat werkt.
          </p>

          <WaitlistForm dark />

          {/* Trust bar */}
          <div className="mt-12 flex flex-wrap justify-center gap-8 text-sm text-slate-500">
            {[
              { val: "500+", label: "leerlingen geholpen" },
              { val: "94%", label: "geslaagd in 1 keer" },
              { val: "8,7", label: "gemiddeld eindcijfer" },
            ].map((s) => (
              <div key={s.label} className="flex items-center gap-2">
                <span className="font-bold text-slate-200">{s.val}</span>
                <span>{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="border-t border-white/5" />

      {/* The feeling */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-black mb-6 leading-snug">
            Je kent dat gevoel wel.
          </h2>
          <p className="text-slate-400 text-lg leading-relaxed mb-6">
            Het examen komt dichterbij. Je zit op je kamer, je aantekeningen voor je, maar het klikt niet.
            Je snapt het in de les — en thuis ben je het weer kwijt.
            Je wil goed presteren, maar je weet niet waar te beginnen.
          </p>
          <p className="text-white text-lg font-medium leading-relaxed">
            Dat is precies waarom SlaagZeker er is.
          </p>
        </div>
      </section>

      {/* How it works */}
      <section id="hoe" className="py-24 px-6 bg-white/[0.02] border-y border-white/5">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Het proces</p>
            <h2 className="text-3xl sm:text-4xl font-black">Van aanmelding tot eindexamen</h2>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Gratis intakegesprek",
                desc: "We leren jou kennen. Welk vak blokkeert je? Hoe leer jij het beste? Samen stellen we vast wat je nodig hebt.",
              },
              {
                step: "02",
                title: "Jouw persoonlijke tutor",
                desc: "We koppelen je aan een tutor die past bij jouw niveau, vak en persoonlijkheid. Iemand die jij begrijpt — en die jou begrijpt.",
              },
              {
                step: "03",
                title: "Oefenen & slagen",
                desc: "Wekelijkse sessies, echte examenopgaven, directe feedback. Elke sessie dichter bij dat eindcijfer waar je op mikt.",
              },
            ].map((item, i) => (
              <div key={item.step} className="relative p-8 rounded-2xl bg-white/[0.03] border border-white/8 group hover:border-violet-500/30 hover:bg-white/[0.05] transition-all">
                <div className="text-6xl font-black text-white/5 mb-5 group-hover:text-violet-500/10 transition-colors">{item.step}</div>
                <div className="w-8 h-[2px] bg-violet-500 mb-5" />
                <h3 className="text-lg font-bold mb-3">{item.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
                {i < 2 && (
                  <div className="hidden sm:block absolute top-12 -right-3 text-slate-600 text-xl">→</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Subjects */}
      <section id="vakken" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Aanbod</p>
            <h2 className="text-3xl sm:text-4xl font-black">12 vakken. Havo & VWO.</h2>
            <p className="text-slate-400 mt-4 max-w-lg mx-auto">Bijles voor alle eindexamenvakken, gegeven door vakspecialisten die recent zelf examen hebben gedaan.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {[
              { vak: "Wiskunde A", icon: "∑" },
              { vak: "Wiskunde B", icon: "∫" },
              { vak: "Wiskunde C", icon: "π" },
              { vak: "Nederlands", icon: "NL" },
              { vak: "Engels", icon: "EN" },
              { vak: "Duits", icon: "DE" },
              { vak: "Frans", icon: "FR" },
              { vak: "Scheikunde", icon: "⚗" },
              { vak: "Natuurkunde", icon: "⚡" },
              { vak: "Biologie", icon: "🧬" },
              { vak: "Economie", icon: "📈" },
              { vak: "Aardrijkskunde", icon: "🌍" },
            ].map(({ vak, icon }) => (
              <div
                key={vak}
                className="flex items-center gap-3 bg-white/[0.03] border border-white/8 rounded-xl px-4 py-4 hover:border-violet-500/30 hover:bg-white/[0.05] transition-all group"
              >
                <span className="text-lg text-slate-500 group-hover:text-violet-400 transition-colors w-6 text-center shrink-0">{icon}</span>
                <span className="text-sm font-medium text-slate-300">{vak}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6 bg-white/[0.02] border-y border-white/5">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Ervaringen</p>
            <h2 className="text-3xl sm:text-4xl font-black">Leerlingen over SlaagZeker</h2>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            {testimonials.map((t) => (
              <div key={t.name} className="flex flex-col p-7 rounded-2xl bg-white/[0.03] border border-white/8">
                <div className="text-violet-400 text-3xl font-serif mb-4 leading-none">"</div>
                <p className="text-slate-300 text-sm leading-relaxed flex-1">{t.quote}</p>
                <div className="mt-6 flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full ${t.color} flex items-center justify-center text-white text-sm font-bold shrink-0`}>
                    {t.initials}
                  </div>
                  <div>
                    <div className="text-sm font-semibold">{t.name}</div>
                    <div className="text-xs text-slate-500">{t.school}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why us */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">Onze aanpak</p>
            <h2 className="text-3xl sm:text-4xl font-black">Niet zomaar bijles</h2>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {[
              {
                title: "Examenspecialisten als tutors",
                desc: "Onze tutors zijn studenten en pas-afgestudeerden die zelf recent eindexamen hebben gedaan. Ze kennen de valkuilen, de puntjes op de i, de examenstijl.",
              },
              {
                title: "Echt persoonlijk — geen groepen",
                desc: "Eén leerling, één tutor. Jij bepaalt het tempo. Geen wachten op anderen, geen stof die je al kent overdoen.",
              },
              {
                title: "Gericht op wat telt",
                desc: "We werken met echte eindexamens, van de afgelopen jaren. Zo wen je aan de vorm, de taal en het niveau.",
              },
              {
                title: "Inzicht, niet uit het hoofd",
                desc: "We leggen uit waaróm iets zo werkt. Want als je het begrijpt, vergeet je het niet meer — ook niet onder druk.",
              },
            ].map((item) => (
              <div key={item.title} className="p-7 rounded-2xl bg-white/[0.03] border border-white/8 hover:border-violet-500/20 transition-all">
                <div className="w-6 h-[2px] bg-violet-500 mb-5" />
                <h3 className="font-bold text-base mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist CTA */}
      <section id="wachtlijst" className="py-28 px-6 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-violet-600/10 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-2xl mx-auto text-center">
          <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-4">Wachtlijst</p>
          <h2 className="text-4xl sm:text-5xl font-black mb-5 leading-tight">
            Jij gaat dit{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
              halen.
            </span>
          </h2>
          <p className="text-slate-400 mb-10 text-lg leading-relaxed">
            Meld je gratis aan. We nemen contact op zodra er plek is — en wie vroeg is, gaat voor.
          </p>
          <WaitlistForm dark />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500">
          <span className="font-black text-white text-lg tracking-tight">
            Slaag<span className="text-violet-400">Zeker</span>
          </span>
          <span>© 2026 SlaagZeker · Alle rechten voorbehouden</span>
          <a href="mailto:hallo@slaagzeker.nl" className="hover:text-slate-300 transition-colors">
            hallo@slaagzeker.nl
          </a>
        </div>
      </footer>
    </div>
  );
}
