"""
Component Library
=================
Pre-built HTML component templates that the Developer agent can reference.
Each component is a Tailwind CSS snippet with placeholders for dynamic content.
"""

COMPONENTS = {
    # ─────────────────────────────────────
    # Hero Variants
    # ─────────────────────────────────────
    "hero_gradient": {
        "name": "Hero — Gradient Overlay",
        "description": "Full-width hero with gradient overlay, headline, subheadline, CTA button, and background image",
        "sections": ["hero"],
        "html_hint": """
<section class="relative min-h-[90vh] flex items-center overflow-hidden">
  <div class="absolute inset-0 bg-gradient-to-br from-{primary}/90 to-{secondary}/80"></div>
  <div class="absolute inset-0">
    <img src="..." class="w-full h-full object-cover" alt="..." loading="lazy">
  </div>
  <div class="relative z-10 max-w-7xl mx-auto px-6 text-white">
    <h1 class="text-5xl md:text-7xl font-bold mb-6 animate-fadeIn">{headline}</h1>
    <p class="text-xl md:text-2xl mb-8 opacity-90 max-w-2xl">{subheadline}</p>
    <a href="#" class="inline-block px-8 py-4 bg-{accent} rounded-full text-lg font-semibold 
       hover:scale-105 transition-transform shadow-xl">{cta_text}</a>
  </div>
</section>""",
    },

    "hero_split": {
        "name": "Hero — Split Layout",
        "description": "Two-column hero with text on left and image/illustration on right",
        "sections": ["hero"],
        "html_hint": """
<section class="min-h-[85vh] flex items-center">
  <div class="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
    <div>
      <h1 class="text-5xl md:text-6xl font-bold mb-6">{headline}</h1>
      <p class="text-xl text-gray-600 mb-8">{subheadline}</p>
      <div class="flex gap-4">
        <a href="#" class="px-8 py-4 bg-{primary} text-white rounded-xl font-semibold
           hover:shadow-lg transition-all">{cta_text}</a>
        <a href="#" class="px-8 py-4 border-2 border-{primary} text-{primary} rounded-xl
           font-semibold hover:bg-{primary}/5 transition-all">Learn More</a>
      </div>
    </div>
    <div class="relative">
      <img src="..." class="rounded-2xl shadow-2xl" alt="...">
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Features Variants
    # ─────────────────────────────────────
    "features_cards": {
        "name": "Features — Card Grid",
        "description": "3-column responsive grid with icon cards, hover lift effect",
        "sections": ["features"],
        "html_hint": """
<section class="py-24 bg-{surface}">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-4">{section_title}</h2>
    <p class="text-center text-gray-600 mb-16 max-w-2xl mx-auto">{section_subtitle}</p>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- repeat for each feature -->
      <div class="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl hover:-translate-y-2 
           transition-all duration-300 group">
        <div class="w-14 h-14 bg-{primary}/10 rounded-xl flex items-center justify-center mb-6
             group-hover:bg-{primary} group-hover:text-white transition-colors">
          <svg>...</svg>
        </div>
        <h3 class="text-xl font-bold mb-3">{feature_title}</h3>
        <p class="text-gray-600">{feature_description}</p>
      </div>
    </div>
  </div>
</section>""",
    },

    "features_alternating": {
        "name": "Features — Alternating Rows",
        "description": "Alternating image-text rows for detailed feature showcase",
        "sections": ["features"],
        "html_hint": """
<section class="py-24">
  <div class="max-w-7xl mx-auto px-6 space-y-32">
    <!-- Feature 1 (image right) -->
    <div class="grid md:grid-cols-2 gap-16 items-center">
      <div>
        <span class="text-{primary} font-semibold uppercase tracking-wider text-sm">Feature 1</span>
        <h3 class="text-3xl font-bold mt-3 mb-6">{feature_title}</h3>
        <p class="text-gray-600 text-lg">{feature_description}</p>
      </div>
      <div><img src="..." class="rounded-2xl shadow-xl" alt="..."></div>
    </div>
    <!-- Feature 2 (image left) — reverse column order -->
    <div class="grid md:grid-cols-2 gap-16 items-center">
      <div class="md:order-2">
        <span class="text-{primary} font-semibold uppercase tracking-wider text-sm">Feature 2</span>
        <h3 class="text-3xl font-bold mt-3 mb-6">{feature_title}</h3>
        <p class="text-gray-600 text-lg">{feature_description}</p>
      </div>
      <div class="md:order-1"><img src="..." class="rounded-2xl shadow-xl" alt="..."></div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Pricing
    # ─────────────────────────────────────
    "pricing_cards": {
        "name": "Pricing — Three Tiers",
        "description": "Three pricing cards with popular plan highlighted",
        "sections": ["pricing"],
        "html_hint": """
<section class="py-24 bg-{surface}">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-4">Simple Pricing</h2>
    <p class="text-center text-gray-600 mb-16">Choose the plan that fits your needs</p>
    <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      <!-- Basic -->
      <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="text-xl font-bold mb-2">Basic</h3>
        <div class="text-4xl font-extrabold mb-6">$9<span class="text-lg text-gray-400">/mo</span></div>
        <ul class="space-y-3 mb-8">
          <li class="flex items-center"><svg class="w-5 h-5 text-green-500 mr-3">✓</svg> Feature 1</li>
        </ul>
        <a href="#" class="block text-center py-3 rounded-xl border-2 border-{primary} text-{primary}
           font-semibold hover:bg-{primary} hover:text-white transition-all">Get Started</a>
      </div>
      <!-- Popular (highlighted) -->
      <div class="bg-{primary} text-white p-8 rounded-2xl shadow-xl relative scale-105">
        <span class="absolute -top-4 left-1/2 -translate-x-1/2 bg-{accent} text-white text-sm 
              font-bold px-4 py-1 rounded-full">Most Popular</span>
        <h3 class="text-xl font-bold mb-2">Pro</h3>
        <div class="text-4xl font-extrabold mb-6">$29<span class="text-lg opacity-60">/mo</span></div>
        <ul class="space-y-3 mb-8">
          <li class="flex items-center"><svg class="w-5 h-5 mr-3">✓</svg> Everything in Basic</li>
        </ul>
        <a href="#" class="block text-center py-3 rounded-xl bg-white text-{primary}
           font-semibold hover:shadow-lg transition-all">Get Started</a>
      </div>
      <!-- Enterprise -->
      <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="text-xl font-bold mb-2">Enterprise</h3>
        <div class="text-4xl font-extrabold mb-6">$99<span class="text-lg text-gray-400">/mo</span></div>
        <ul class="space-y-3 mb-8">
          <li class="flex items-center"><svg class="w-5 h-5 text-green-500 mr-3">✓</svg> Everything in Pro</li>
        </ul>
        <a href="#" class="block text-center py-3 rounded-xl border-2 border-{primary} text-{primary}
           font-semibold hover:bg-{primary} hover:text-white transition-all">Contact Us</a>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Testimonials
    # ─────────────────────────────────────
    "testimonials_cards": {
        "name": "Testimonials — Card Grid",
        "description": "Three testimonial cards with avatar, name, role, and quote",
        "sections": ["testimonials"],
        "html_hint": """
<section class="py-24">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-16">What Our Clients Say</h2>
    <div class="grid md:grid-cols-3 gap-8">
      <div class="bg-{surface} p-8 rounded-2xl relative">
        <div class="text-6xl text-{primary}/20 absolute top-4 left-6">"</div>
        <p class="text-gray-600 mb-6 relative z-10 pt-8">{testimonial_text}</p>
        <div class="flex items-center gap-4">
          <img src="..." class="w-12 h-12 rounded-full object-cover" alt="...">
          <div>
            <div class="font-bold">{name}</div>
            <div class="text-sm text-gray-500">{role}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # FAQ
    # ─────────────────────────────────────
    "faq_accordion": {
        "name": "FAQ — Accordion",
        "description": "Expandable FAQ with smooth animations",
        "sections": ["faq"],
        "html_hint": """
<section class="py-24 bg-{surface}">
  <div class="max-w-3xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-16">Frequently Asked Questions</h2>
    <div class="space-y-4">
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">
        <button onclick="this.parentElement.classList.toggle('active')"
                class="w-full px-6 py-5 text-left font-semibold flex justify-between items-center">
          <span>{question}</span>
          <svg class="w-5 h-5 transition-transform" viewBox="0 0 20 20" fill="currentColor">
            <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
          </svg>
        </button>
        <div class="px-6 pb-5 text-gray-600 hidden">{answer}</div>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Stats / Social Proof
    # ─────────────────────────────────────
    "stats_counter": {
        "name": "Stats — Counter Bar",
        "description": "Horizontal stat counters with large numbers",
        "sections": ["stats"],
        "html_hint": """
<section class="py-16 bg-{primary}">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
      <div>
        <div class="text-4xl md:text-5xl font-extrabold mb-2">500+</div>
        <div class="text-sm uppercase tracking-wider opacity-80">Happy Clients</div>
      </div>
      <div>
        <div class="text-4xl md:text-5xl font-extrabold mb-2">10K+</div>
        <div class="text-sm uppercase tracking-wider opacity-80">Projects Done</div>
      </div>
      <div>
        <div class="text-4xl md:text-5xl font-extrabold mb-2">99%</div>
        <div class="text-sm uppercase tracking-wider opacity-80">Satisfaction</div>
      </div>
      <div>
        <div class="text-4xl md:text-5xl font-extrabold mb-2">24/7</div>
        <div class="text-sm uppercase tracking-wider opacity-80">Support</div>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # CTA
    # ─────────────────────────────────────
    "cta_gradient": {
        "name": "CTA — Gradient Banner",
        "description": "Full-width gradient call-to-action section",
        "sections": ["cta"],
        "html_hint": """
<section class="py-24 bg-gradient-to-br from-{primary} to-{secondary}">
  <div class="max-w-4xl mx-auto px-6 text-center text-white">
    <h2 class="text-4xl md:text-5xl font-bold mb-6">{cta_heading}</h2>
    <p class="text-xl opacity-90 mb-10 max-w-2xl mx-auto">{cta_text}</p>
    <a href="#" class="inline-block px-10 py-4 bg-white text-{primary} rounded-full 
       text-lg font-bold hover:shadow-2xl hover:scale-105 transition-all">{button_text}</a>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Contact
    # ─────────────────────────────────────
    "contact_form": {
        "name": "Contact — Form with Map",
        "description": "Contact form with details sidebar",
        "sections": ["contact"],
        "html_hint": """
<section class="py-24">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-16">Get In Touch</h2>
    <div class="grid md:grid-cols-2 gap-16">
      <form class="space-y-6">
        <div class="grid md:grid-cols-2 gap-6">
          <input type="text" placeholder="First Name" class="w-full px-4 py-3 rounded-xl border
                 border-gray-200 focus:border-{primary} focus:ring-2 focus:ring-{primary}/20 outline-none">
          <input type="text" placeholder="Last Name" class="w-full px-4 py-3 rounded-xl border
                 border-gray-200 focus:border-{primary} focus:ring-2 focus:ring-{primary}/20 outline-none">
        </div>
        <input type="email" placeholder="Email" class="w-full px-4 py-3 rounded-xl border
               border-gray-200 focus:border-{primary} focus:ring-2 focus:ring-{primary}/20 outline-none">
        <textarea placeholder="Message" rows="4" class="w-full px-4 py-3 rounded-xl border
                  border-gray-200 focus:border-{primary} focus:ring-2 focus:ring-{primary}/20 outline-none"></textarea>
        <button class="w-full py-4 bg-{primary} text-white rounded-xl font-semibold
                hover:shadow-lg transition-all">Send Message</button>
      </form>
      <div class="space-y-8">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-{primary}/10 rounded-xl flex items-center justify-center shrink-0">📍</div>
          <div><h4 class="font-bold">Address</h4><p class="text-gray-600">{address}</p></div>
        </div>
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-{primary}/10 rounded-xl flex items-center justify-center shrink-0">📧</div>
          <div><h4 class="font-bold">Email</h4><p class="text-gray-600">{email}</p></div>
        </div>
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-{primary}/10 rounded-xl flex items-center justify-center shrink-0">📞</div>
          <div><h4 class="font-bold">Phone</h4><p class="text-gray-600">{phone}</p></div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Footer
    # ─────────────────────────────────────
    "footer_multi_column": {
        "name": "Footer — Multi-Column",
        "description": "Professional multi-column footer with links and social icons",
        "sections": ["footer"],
        "html_hint": """
<footer class="bg-gray-900 text-white pt-20 pb-8">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid md:grid-cols-4 gap-12 mb-16">
      <div>
        <h3 class="text-2xl font-bold mb-4">{brand_name}</h3>
        <p class="text-gray-400">{footer_tagline}</p>
        <div class="flex gap-4 mt-6">
          <a href="#" class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center 
             hover:bg-{primary} transition-colors">...</a>
        </div>
      </div>
      <div>
        <h4 class="font-bold mb-4 uppercase tracking-wider text-sm">Product</h4>
        <ul class="space-y-3 text-gray-400">
          <li><a href="#" class="hover:text-white transition-colors">Features</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Pricing</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-bold mb-4 uppercase tracking-wider text-sm">Company</h4>
        <ul class="space-y-3 text-gray-400">
          <li><a href="#" class="hover:text-white transition-colors">About</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-bold mb-4 uppercase tracking-wider text-sm">Legal</h4>
        <ul class="space-y-3 text-gray-400">
          <li><a href="#" class="hover:text-white transition-colors">Privacy</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Terms</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-gray-800 pt-8 text-center text-gray-500">
      <p>&copy; 2025 {brand_name}. All rights reserved.</p>
    </div>
  </div>
</footer>""",
    },

    # ─────────────────────────────────────
    # Gallery
    # ─────────────────────────────────────
    "gallery_masonry": {
        "name": "Gallery — Masonry Grid",
        "description": "Masonry-style image gallery with hover overlay",
        "sections": ["gallery"],
        "html_hint": """
<section class="py-24">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-16">{gallery_title}</h2>
    <div class="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
      <div class="break-inside-avoid relative group overflow-hidden rounded-2xl">
        <img src="..." class="w-full group-hover:scale-110 transition-transform duration-500" alt="...">
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 
             group-hover:opacity-100 transition-opacity flex items-end p-6">
          <span class="text-white font-semibold">{caption}</span>
        </div>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Team
    # ─────────────────────────────────────
    "team_grid": {
        "name": "Team — Photo Grid",
        "description": "Team member cards with photo, name, and role",
        "sections": ["team"],
        "html_hint": """
<section class="py-24 bg-{surface}">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-4">Meet Our Team</h2>
    <p class="text-center text-gray-600 mb-16 max-w-2xl mx-auto">The people behind the magic</p>
    <div class="grid md:grid-cols-3 lg:grid-cols-4 gap-8">
      <div class="text-center group">
        <div class="relative overflow-hidden rounded-2xl mb-4">
          <img src="..." class="w-full aspect-square object-cover group-hover:scale-105 
               transition-transform duration-300" alt="...">
        </div>
        <h4 class="font-bold text-lg">{member_name}</h4>
        <p class="text-{primary}">{member_role}</p>
      </div>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Blog / News
    # ─────────────────────────────────────
    "blog_cards": {
        "name": "Blog — Card Grid",
        "description": "Three blog post cards with image, date, title, excerpt, and read more link",
        "sections": ["blog"],
        "html_hint": """
<section class="py-24">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-4">Latest Articles</h2>
    <p class="text-center text-gray-600 mb-16">Insights, tips, and industry news</p>
    <div class="grid md:grid-cols-3 gap-8">
      <article class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-shadow group">
        <div class="overflow-hidden">
          <img src="..." class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500" alt="...">
        </div>
        <div class="p-6">
          <span class="text-sm text-{primary} font-semibold">Category</span>
          <span class="text-sm text-gray-400 ml-2">Jan 15, 2026</span>
          <h3 class="text-xl font-bold mt-2 mb-3">{post_title}</h3>
          <p class="text-gray-600 mb-4">{post_excerpt}</p>
          <a href="#" class="text-{primary} font-semibold hover:underline inline-flex items-center gap-1">
            Read More <span>→</span>
          </a>
        </div>
      </article>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Video Hero
    # ─────────────────────────────────────
    "hero_video": {
        "name": "Hero — Video Background",
        "description": "Full-screen hero with looping background video, dark overlay, and centered CTA",
        "sections": ["hero"],
        "html_hint": """
<section class="relative min-h-screen flex items-center justify-center overflow-hidden">
  <video autoplay muted loop playsinline class="absolute inset-0 w-full h-full object-cover">
    <source src="..." type="video/mp4">
  </video>
  <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/70"></div>
  <div class="relative z-10 text-center text-white max-w-4xl mx-auto px-6">
    <h1 class="text-5xl md:text-7xl font-bold mb-6 leading-tight">{headline}</h1>
    <p class="text-xl md:text-2xl mb-10 opacity-90 max-w-2xl mx-auto">{subheadline}</p>
    <div class="flex gap-4 justify-center">
      <a href="#" class="px-10 py-4 bg-{primary} rounded-full text-lg font-semibold 
         hover:scale-105 transition-transform shadow-xl">{cta_text}</a>
      <a href="#" class="px-10 py-4 border-2 border-white rounded-full text-lg font-semibold
         hover:bg-white/10 transition-colors">Watch Demo</a>
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Logo Cloud / Partners
    # ─────────────────────────────────────
    "logo_cloud": {
        "name": "Logo Cloud — Trusted By",
        "description": "Row of partner/client logos with 'Trusted By' heading and grayscale hover effect",
        "sections": ["logos", "partners"],
        "html_hint": """
<section class="py-16 border-y border-gray-100">
  <div class="max-w-7xl mx-auto px-6">
    <p class="text-center text-gray-400 uppercase tracking-wider text-sm font-semibold mb-10">
      Trusted by leading companies
    </p>
    <div class="flex flex-wrap justify-center items-center gap-12 md:gap-16">
      <img src="..." class="h-8 md:h-10 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 
           transition-all duration-300" alt="Partner 1">
      <img src="..." class="h-8 md:h-10 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 
           transition-all duration-300" alt="Partner 2">
      <img src="..." class="h-8 md:h-10 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 
           transition-all duration-300" alt="Partner 3">
      <img src="..." class="h-8 md:h-10 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 
           transition-all duration-300" alt="Partner 4">
      <img src="..." class="h-8 md:h-10 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 
           transition-all duration-300" alt="Partner 5">
    </div>
  </div>
</section>""",
    },

    # ─────────────────────────────────────
    # Comparison Table
    # ─────────────────────────────────────
    "comparison_table": {
        "name": "Comparison — Feature Table",
        "description": "Side-by-side comparison table highlighting your product vs competitors",
        "sections": ["comparison", "features"],
        "html_hint": """
<section class="py-24 bg-{surface}">
  <div class="max-w-5xl mx-auto px-6">
    <h2 class="text-4xl font-bold text-center mb-4">Why Choose Us</h2>
    <p class="text-center text-gray-600 mb-16">See how we compare</p>
    <div class="overflow-x-auto">
      <table class="w-full text-left">
        <thead>
          <tr class="border-b-2 border-gray-200">
            <th class="py-4 px-6 font-semibold text-gray-500">Feature</th>
            <th class="py-4 px-6 font-bold text-{primary} bg-{primary}/5 rounded-t-xl">Our Product</th>
            <th class="py-4 px-6 font-semibold text-gray-500">Competitor A</th>
            <th class="py-4 px-6 font-semibold text-gray-500">Competitor B</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr>
            <td class="py-4 px-6 font-medium">{feature_name}</td>
            <td class="py-4 px-6 bg-{primary}/5 text-green-600 font-semibold">✓</td>
            <td class="py-4 px-6 text-red-400">✗</td>
            <td class="py-4 px-6 text-gray-400">Partial</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>""",
    },
}


def get_component_hints_for_sections(sections: list) -> str:
    """Get component HTML hints for the requested sections."""
    hints = []
    for section in sections:
        matching = [
            comp for comp in COMPONENTS.values()
            if section in comp["sections"]
        ]
        if matching:
            # Pick the first (default) variant
            comp = matching[0]
            hints.append(f"### {comp['name']}\n{comp['html_hint']}")
    return "\n\n".join(hints)


def get_available_components() -> dict:
    """Return all available components grouped by section."""
    grouped = {}
    for key, comp in COMPONENTS.items():
        for section in comp["sections"]:
            if section not in grouped:
                grouped[section] = []
            grouped[section].append({"key": key, "name": comp["name"], "desc": comp["description"]})
    return grouped
