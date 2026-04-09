"use client";

import { useState } from "react";

function WaitlistForm({ id }: { id: string }) {
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
      <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
        <div className="text-4xl mb-3">🎉</div>
        <h3 className="text-xl font-bold text-green-800 mb-2">
          Je staat op de wachtlijst!
        </h3>
        <p className="text-green-700">
          We nemen snel contact met je op. Klaar voor je eindexamen!
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} id={id} className="flex flex-col gap-3 w-full max-w-md mx-auto">
      <input
        type="text"
        placeholder="Je voornaam"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        className="w-full px-5 py-4 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-400 text-base"
      />
      <input
        type="email"
        placeholder="Je e-mailadres"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        className="w-full px-5 py-4 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-400 text-base"
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white font-bold py-4 px-8 rounded-xl text-base transition-colors cursor-pointer"
      >
        {loading ? "Bezig..." : "Zet me op de wachtlijst →"}
      </button>
      <p className="text-xs text-slate-400 text-center">
        Gratis. Geen spam. Uitschrijven wanneer je wilt.
      </p>
    </form>
  );
}

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-white text-slate-900">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-sm border-b border-slate-100">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-2xl font-black text-slate-900">
            Slaag<span className="text-orange-500">Zeker</span>
          </span>
          <a
            href="#wachtlijst"
            className="bg-orange-500 hover:bg-orange-600 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition-colors"
          >
            Wachtlijst
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block bg-orange-500/20 text-orange-400 text-sm font-semibold px-4 py-1.5 rounded-full mb-6">
            Eindexamen 2026 — schrijf je nu in
          </div>
          <h1 className="text-5xl sm:text-6xl font-black leading-tight mb-6">
            Slaag zeker voor je{" "}
            <span className="text-orange-400">eindexamen</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            Persoonlijke bijles voor havo- en vwo-scholieren. Wij zorgen dat je
            precies weet wat je moet kennen — en dat je het ook echt begrijpt.
          </p>
          <WaitlistForm id="hero-form" />
        </div>
      </section>

      {/* Social proof stats */}
      <section className="py-16 px-6 bg-orange-50 border-y border-orange-100">
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          {[
            { number: "500+", label: "Leerlingen geholpen" },
            { number: "94%", label: "Geslaagd in 1 keer" },
            { number: "8,7", label: "Gemiddeld cijfer" },
            { number: "12", label: "Vakken beschikbaar" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-4xl font-black text-orange-500">{stat.number}</div>
              <div className="text-slate-600 text-sm mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-center mb-4">Hoe het werkt</h2>
          <p className="text-slate-500 text-center mb-12 max-w-xl mx-auto">
            Van aanmelding tot eindexamen in drie stappen
          </p>
          <div className="grid sm:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Intake gesprek",
                desc: "We brengen jouw niveau, leerpunten en doelen in kaart. Gratis en vrijblijvend.",
              },
              {
                step: "02",
                title: "Persoonlijk plan",
                desc: "Je krijgt een studieroute op maat — gericht op precies de stof die jij nodig hebt.",
              },
              {
                step: "03",
                title: "Oefenen & slagen",
                desc: "Wekelijkse sessies met een vaste tutor, echte examentraining en directe feedback.",
              },
            ].map((item) => (
              <div key={item.step} className="relative p-8 rounded-2xl border border-slate-100 bg-slate-50">
                <div className="text-5xl font-black text-slate-100 mb-4">{item.step}</div>
                <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Subjects */}
      <section className="py-20 px-6 bg-slate-900 text-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-center mb-4">Vakken</h2>
          <p className="text-slate-400 text-center mb-12 max-w-xl mx-auto">
            Bijles voor alle populaire eindexamenvakken, voor zowel havo als vwo
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {[
              "Wiskunde A",
              "Wiskunde B",
              "Wiskunde C",
              "Nederlands",
              "Engels",
              "Duits",
              "Frans",
              "Scheikunde",
              "Natuurkunde",
              "Biologie",
              "Economie",
              "Aardrijkskunde",
            ].map((vak) => (
              <div
                key={vak}
                className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm font-medium text-slate-200 text-center"
              >
                {vak}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why SlaagZeker */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-center mb-4">Waarom SlaagZeker?</h2>
          <p className="text-slate-500 text-center mb-12 max-w-xl mx-auto">
            Niet zomaar bijles — gerichte voorbereiding die werkt
          </p>
          <div className="grid sm:grid-cols-2 gap-6">
            {[
              {
                icon: "🎯",
                title: "Gericht op het eindexamen",
                desc: "Onze tutors kennen de examenprogramma's door en door. Geen onnodige theorie — alleen wat telt.",
              },
              {
                icon: "👤",
                title: "Vaste tutor, echte band",
                desc: "Je werkt altijd met dezelfde tutor. Die kent jouw valkuilen, jouw tempo, jouw doelen.",
              },
              {
                icon: "📅",
                title: "Flexibel inplannen",
                desc: "Online of op locatie, overdag of 's avonds. Jij bepaalt wanneer het past.",
              },
              {
                icon: "📊",
                title: "Voortgang inzichtelijk",
                desc: "Na elke sessie weet je precies waar je staat en wat de volgende stap is.",
              },
            ].map((item) => (
              <div key={item.title} className="flex gap-5 p-6 rounded-2xl border border-slate-100">
                <span className="text-3xl shrink-0">{item.icon}</span>
                <div>
                  <h3 className="font-bold mb-1">{item.title}</h3>
                  <p className="text-slate-500 text-sm leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-orange-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-center mb-12">
            Wat leerlingen zeggen
          </h2>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                quote:
                  "Ik dacht dat ik wiskunde gewoon niet snapte. Na 6 weken SlaagZeker had ik een 7,5 op mijn eindexamen.",
                name: "Sanne, havo 5",
              },
              {
                quote:
                  "Mijn tutor wist precies waar ik moeite mee had. De sessies waren intensief maar het heeft echt geholpen.",
                name: "Tim, vwo 6",
              },
              {
                quote:
                  "Eindelijk bijles die aanvoelt alsof iemand echt begrijpt hoe je leert. Dank jullie wel!",
                name: "Fatima, havo 5",
              },
            ].map((t) => (
              <div key={t.name} className="bg-white rounded-2xl p-6 shadow-sm border border-orange-100">
                <div className="text-orange-400 text-2xl mb-3">"</div>
                <p className="text-slate-700 text-sm leading-relaxed mb-4">{t.quote}</p>
                <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                  {t.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist CTA */}
      <section id="wachtlijst" className="py-24 px-6 bg-slate-900 text-white">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-4xl font-black mb-4">
            Klaar voor jouw{" "}
            <span className="text-orange-400">eindexamen</span>?
          </h2>
          <p className="text-slate-300 mb-10 text-lg">
            Meld je aan voor de wachtlijst. We nemen contact op zodra er plek is — en we geven voorrang aan vroege aanmeldingen.
          </p>
          <WaitlistForm id="waitlist-form" />
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-100">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-400">
          <span className="font-black text-slate-900 text-lg">
            Slaag<span className="text-orange-500">Zeker</span>
          </span>
          <span>© 2026 SlaagZeker. Alle rechten voorbehouden.</span>
          <a href="mailto:hallo@slaagzeker.nl" className="hover:text-slate-700 transition-colors">
            hallo@slaagzeker.nl
          </a>
        </div>
      </footer>
    </div>
  );
}
