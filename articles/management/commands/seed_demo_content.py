import random
import textwrap
from datetime import timedelta
from io import BytesIO

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from articles.models import (
    Article,
    ArticleComment,
    ArticleReaction,
    Bookmark,
    Category,
    CATEGORY_FALLBACK_COVERS,
)
from PIL import Image, ImageDraw, ImageFont


CATEGORY_IMAGE_SOURCES = {
    "Backend": [
        CATEGORY_FALLBACK_COVERS["Backend"],
        "https://images.unsplash.com/photo-1517433456452-f9633a875f6f",
    ],
    "Frontend": [
        CATEGORY_FALLBACK_COVERS["Frontend"],
        "https://images.unsplash.com/photo-1454165205744-3b78555e5572",
    ],
    "AI": [
        CATEGORY_FALLBACK_COVERS["AI"],
        "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d",
    ],
    "Cyber Security": [
        CATEGORY_FALLBACK_COVERS["Cyber Security"],
        "https://images.unsplash.com/photo-1555949963-aa79dcee981c",
    ],
    "Cyber Sport": [
        CATEGORY_FALLBACK_COVERS["Cyber Sport"],
        "https://images.unsplash.com/photo-1517649763962-0c623066013b",
    ],
    "Game Development": [
        CATEGORY_FALLBACK_COVERS["Game Development"],
        "https://images.unsplash.com/photo-1545239351-1141bd82e8a6",
    ],
}

COMMENT_SNIPPETS = [
    "Loved the detailed explanation around {topic}. We followed a similar playbook last quarter and saw huge wins.",
    "This is the kind of pragmatic write-up I send to my team. Thanks for highlighting the trade-offs.",
    "Curious how you see this scaling as the organisation grows--still debating the approach in our shop.",
    "Solid breakdown. The metrics you shared make a great benchmark for us to compare against.",
    "Appreciate the transparency about what went wrong. Too many posts gloss over the painful bits.",
]


ARTICLE_DATA = [
    {
        "category": "Backend",
        "title": "Designing Resilient Microservices on PostgreSQL 16",
        "summary": "Lessons learned while decomposing a legacy monolith and adopting logical replication in PostgreSQL 16.",
        "body": [
            "Over the past eighteen months our payments platform migrated from a nine-year-old monolith to a constellation of twelve Go services. The biggest architectural risk was our shared Postgres database. Until recently, our strategy hinged on sharding, but Postgres 16 shipped logical replication improvements that gave us a cleaner way to decouple schema ownership.",
            "We began by isolating the event-sourcing pipeline. Each service published domain events into a dedicated schema, while consumers subscribed through logical replication slots. Because replication is asynchronous, we introduced an idempotent write layer to avoid double processing should a slot fall behind during deployments.",
            "The largest surprise involved vacuum pressure. Logical replication retains WAL segments longer than physical replication, so we expanded storage and tuned `max_slot_wal_keep_size`. Without that adjustment the replica lag spiked after a bulk import. We also added auto scaling for the logical subscribers, leveraging KEDA metrics to scale on replication lag.",
            "The end result is a topology where every domain team owns its schema, yet we still preserve relational guarantees. If you're bracing for a microservice split in 2025, evaluate Postgres 16's logical replication early--it may save months of cross-team coordination."
        ],
        "status": "published",
    },
    {
        "category": "Backend",
        "title": "gRPC vs. Async REST: Choosing the Right Wire Protocol for Internal APIs",
        "summary": "A benchmark-driven comparison of gRPC and modern async REST stacks when latency, observability, and tooling all matter.",
        "body": [
            "Internal service-to-service calls account for 87% of the traffic inside our infrastructure. We ran a ten-day benchmark comparing our existing REST stack--FastAPI behind Envoy--with a gRPC prototype written in Kotlin. The workload simulated fifty million requests per day with a 90/10 read/write split.",
            "gRPC delivered a 37% reduction in median latency and cut serialized payload size roughly in half. That matters when you shard across availability zones. However, we underestimated the developer experience gap. JSON payloads are trivial to inspect, but protobuf messages required additional observability tooling and more training during on-call escalations.",
            "Ultimately we adopted a hybrid model. High-volume, low-touch services now expose a gRPC surface, while endpoints that interact with third parties remain REST. The key is documenting ownership boundaries early so teams can converge on a tooling baseline instead of supporting every protocol under the sun."
        ],
        "status": "published",
    },
    {
        "category": "Backend",
        "title": "Lessons from Shipping Serverless Batch Jobs on Cloud Run",
        "summary": "Serverless batch looks effortless on slides. Here is the sober list of constraints we hit once workloads crossed 300k executions a day.",
        "body": [
            "The promise of Cloud Run jobs is seductive--containerized workloads without VM management. We ported our nightly ETL pipeline in two weeks, but production traffic exposed several sharp edges. Cold starts in particular ballooned when the runtime pulled large container images; slimming images to sub-200MB cut average start time by 44%.",
            "Retry semantics proved tricky. Cloud Run marks a job as failed after three retries even if failures were caused by downstream rate limits. Our workaround was to implement compensating logic in Pub/Sub and reschedule jobs rather than relying solely on Cloud Run's retries.",
            "My advice: treat serverless batch like any other production system. Instrument aggressively, version container images, and keep Terraform definitions close to the workloads they control. You give up manual server management but inherit a different set of operational muscles."
        ],
        "status": "published",
    },
    {
        "category": "Frontend",
        "title": "Progressive Enhancement with Server Components and Islands",
        "summary": "A pragmatic blueprint for teams straddling legacy SSR and modern React Server Components without losing accessibility.",
        "body": [
            "Our marketing platform must serve millions of visitors on sub-3G networks. We adopted an 'islands of interactivity' approach built on Astro and React Server Components. Static HTML renders instantly, while interactive islands hydrate progressively based on viewport intersection observers.",
            "Accessibility was the north star. Instead of polyfilling everything, we rely on semantic HTML and sprinkle enhancements only when the browser reports sufficient capabilities. This dramatically reduced JS bundle size--down to 48KB gzipped for the homepage--and core web vitals improved across the board.",
            "If you're migrating from a React SPA, resist the temptation to ship a parallel client bundle. Start by identifying components that truly need interactivity, then let the rest render server-side. Your lighthouse score--and your users--will thank you."
        ],
        "status": "published",
    },
    {
        "category": "Frontend",
        "title": "Design Tokens at Scale: How We Rebuilt Our UI System in 6 Weeks",
        "summary": "Migrating 60+ applications to a unified design token pipeline powered by Style Dictionary and vanilla-extract.",
        "body": [
            "Our previous design system relied on Sass variables that drifted across repositories. We centralized tokens in a JSON schema processed by Style Dictionary, emitting platform-specific outputs for web, iOS, and Android. The tricky part was orchestrating updates without breaking consumer apps.",
            "We implemented semantic versioning for the token package and used changesets to track modifications. To minimize regressions, we wired visual regression tests with Chromatic snapshots. The rollout uncovered dozens of inaccessible color combinations that were quietly harming contrast ratios.",
            "Six weeks later every surface area--from marketing landing pages to the internal admin console--consumes the same token pipeline. The benefits show up in velocity: designers iterate once, and implementation-ready artifacts flow automatically to product teams."
        ],
        "status": "published",
    },
    {
        "category": "Frontend",
        "title": "Why the Next Generation of Dashboards Belongs to WebGPU",
        "summary": "An early look at prototyping analytic dashboards with WebGPU and React Three Fiber for sub-10ms rendering.",
        "body": [
            "Data visualization at enterprise scale often hits canvas performance ceilings. We built a prototype using WebGPU via the wgpu native bindings. On a dataset with 1.2 million points, WebGPU rendered aggregations in 8.6ms compared to 32ms on WebGL and over 110ms with SVG.",
            "Of course, WebGPU is still experimental. Driver support remains inconsistent and the learning curve is steep. We mitigated the risk by providing a graceful fallback to canvas rendering whenever WebGPU initialization fails.",
            "If your audience includes power users on modern browsers, investing in WebGPU today protects your dashboards for the next five years. Just budget time for developer education--thinking in compute shaders is a paradigm shift for most front-end teams."
        ],
        "status": "pending",
    },
    {
        "category": "AI",
        "title": "From Retrieval-Augmented Generation to Grounded Action: Shipping AI Ops Assistants",
        "summary": "How we combined RAG, event streams, and guardrails to ship a reliable AI assistant for SRE runbooks.",
        "body": [
            "RAG alone rarely delivers trustworthy automation. Our SRE assistant fuses retrieval with a policy graph. Each suggested remediation references a concrete runbook step, tracks the originating incident, and requires human confirmation before execution.",
            "We embedded observability metadata--Grafana dashboards, PagerDuty incidents, and Kibana traces--into a vector store. The assistant retrieves contextual documents, then a rules engine determines whether the action stays advisory or escalates to an automated workflow via Argo Workflows.",
            "The project surfaced ethical questions. We introduced a 'decision ledger' that records every AI suggestion and the human response. This transparency proved essential during postmortems. If you're building AI copilots for ops teams, plan for auditability from day zero."
        ],
        "status": "published",
    },
    {
        "category": "AI",
        "title": "Evaluating Open-Weight Models for On-Prem Inference in 2025",
        "summary": "Benchmarks across Llama 3, Mistral Medium, and Cohere Command R+ with a focus on latency, context windows, and TCO.",
        "body": [
            "Many regulated industries still require on-prem inference. We ran an exhaustive comparison of current open-weight contenders on our A100 cluster. Llama 3 70B delivered the best reasoning scores but required aggressive quantization to meet latency targets. Mistral Medium offered a sweet spot between quality and cost once distilled to 8-bit.",
            "Context windows remain a decisive differentiator. Cohere Command R+ handled 128k tokens flawlessly, making it ideal for large contract analysis. However, its GPU appetite was high enough that we reserved it for batch workloads rather than synchronous chat.",
            "Total cost of ownership favored Mistral Medium, especially when paired with FlashAttention 2 kernels. If you're pursuing hybrid cloud AI, break down workloads by context window and latency requirements before committing to a model family."
        ],
        "status": "published",
    },
    {
        "category": "AI",
        "title": "Fine-Tuning Vision Transformers for Industrial Defect Detection",
        "summary": "A case study on distilling foundation models into efficient inspectors for manufacturing lines.",
        "body": [
            "We partnered with an automotive supplier to detect paint defects in near-real time. Starting from a SAM-based foundation model, we distilled features into a compact ViT-S architecture. The pipeline leverages edge TPUs, so inference stays under 40ms per frame.",
            "Data quality mattered more than model architecture. We built a synthetic augmentation kit that mimicked dust contamination and lighting variations using Blender. The augmented dataset reduced false positives by 22% without requiring additional annotation passes.",
            "Deploying to the plant introduced a new challenge: operators needed an explanation interface. We overlaid heatmaps directly on the inspection feeds and surfaced top contributing pixels. Transparency built trust, and the client greenlit expanding the system to three more production lines."
        ],
        "status": "published",
    },
    {
        "category": "Cyber Security",
        "title": "Defending Managed Kubernetes Clusters from Lateral Movement",
        "summary": "A red-team simulation showed how easy it is to pivot from a compromised pod. Here is the mitigation playbook that actually worked.",
        "body": [
            "Our red team compromised a development pod through an outdated npm package. From there they attempted to pivot into the control plane. Network policies stopped the initial attempts, but we discovered that lingering service account tokens provided broader access than intended.",
            "We applied three countermeasures: short-lived service account tokens enforced by projected volumes, runtime enforcement via Kyverno, and continuous posture scanning with Open Policy Agent. Combining the trio reduced the blast radius dramatically.",
            "Kubernetes security is a treadmill. Make posture scanning part of CI, rotate credentials weekly, and treat the cluster as a zero-trust environment regardless of whether it lives in dev or prod."
        ],
        "status": "published",
    },
    {
        "category": "Cyber Security",
        "title": "The Real Cost of MFA Fatigue Attacks",
        "summary": "We analyzed six months of incident data to quantify how MFA fatigue attacks bypassed human vigilance and what countermeasures stuck.",
        "body": [
            "Attackers aren't giving up on push fatigue. Our incident response logs recorded 43 attempts in six months, with a 12% success rate when the target was tired or multitasking. Education alone isn't enough.",
            "We rolled out number matching, throttled push notifications, and implemented conditional access based on device health. The combination cut successful attempts to zero so far. The missing link was observability: we built dashboards that correlate failed pushes with login geography to spot patterns early.",
            "You can't expect employees to stay vigilant forever. Design MFA flows that minimize interruptions and introduce friction only when risk spikes."
        ],
        "status": "published",
    },
    {
        "category": "Cyber Security",
        "title": "Why SBOMs Still Matter After the Hype Cycle",
        "summary": "Shipping software bills of materials is now table stakes. Here is how we automated SBOM generation and verification without slowing pipelines.",
        "body": [
            "Regulators worldwide are eyeing SBOM adoption. We automated SBOM creation using Syft and attested artifacts with Cosign. The key was embedding SBOM generation into the build step so developers couldn't bypass it inadvertently.",
            "Verification happens downstream. Admission controllers reject containers lacking a signed SBOM, and our internal marketplace surfaces dependency vulnerabilities automatically. Developers initially grumbled, but the workflow saved us during the recent glibc CVE scramble.",
            "If SBOMs feel like bureaucratic overhead, reframe them as the inventory system you wish you had during your last incident. Automation keeps morale intact while satisfying incoming compliance mandates."
        ],
        "status": "pending",
    },
    {
        "category": "Cyber Sport",
        "title": "How Tactical Timeouts Reshaped Valorant Masters Tokyo",
        "summary": "An analytical deep dive into why teams that mastered timeout usage outperformed their seeds.",
        "body": [
            "Timeout usage in Valorant isn't just about calming nerves. Reviewing Masters Tokyo demos, we saw that victorious teams gained an average of 1.7 rounds immediately after a timeout. Coaches used the pause to reset defaults and call audacious site hits that punished aggressive defenders.",
            "Paper Rex popularized staggered timeout strategies--burning a pause even after a won round to bank tactical momentum. Expect more teams to treat timeouts as chess clocks rather than emergency brakes.",
            "If you're coaching at any tier, script timeout scenarios into scrims. Players should know exactly which set piece to execute when the coach pushes the pause button."
        ],
        "status": "published",
    },
    {
        "category": "Cyber Sport",
        "title": "The Scouting Stack Behind Tier-One Dota Rosters",
        "summary": "From replay parsers to private AI scrim assistants, modern esports scouting looks a lot like pro sports analytics.",
        "body": [
            "Top teams ingest terabytes of scrim data weekly. We built a scouting stack combining OpenDota APIs, custom replay parsers, and an internal LLM that surfaces draft anomalies. Analysts query natural language prompts--“show me every offlane Beastmaster timing with Helm rush in patch 7.35”--and get frame-accurate clips.",
            "Culture change mattered as much as tooling. Coaches shared dashboards with players so they could self-scout between practice blocks. The shared context shortened feedback loops and prevented conflicts over subjective impressions.",
            "If your org still relies on spreadsheets, start automating data collection. Even a lightweight pipeline that tags power spikes can yield competitive edges during playoff prep."
        ],
        "status": "published",
    },
    {
        "category": "Cyber Sport",
        "title": "Mental Skills Coaches Are the Secret Weapon in CS2",
        "summary": "A look at how elite CS2 rosters embed sports psychology into daily practice routines.",
        "body": [
            "The shift to CS2 reignited conversations around tilt management. Organizations like Heroic and G2 now retain full-time mental skills coaches. Sessions cover breathing drills, post-round reframing, and structured peer feedback.",
            "Performance data backs it up. Teams that introduced mental coaching cut eco-round collapses by 19% across an entire split. Players reported higher confidence entering map deciders, reducing the need for dramatic roster changes mid-season.",
            "Aspiring pros: treat mental conditioning like aim training. The teams investing in psychology today will dominate LANs once the CS2 meta stabilizes."
        ],
        "status": "published",
    },
    {
        "category": "Game Development",
        "title": "Shipping DLSS 3.5 and FSR 3 in the Same Rendering Engine",
        "summary": "Supporting competing frame generation technologies forced us to rethink our abstraction layers.",
        "body": [
            "Players demand choice, so our AAA title supports both DLSS 3.5 and FSR 3. The challenge was organizing the render pipeline to accommodate NVIDIA's Frame Generation while still honoring AMD's shader path. We created a unified temporal reconstruction interface that plugs into either vendor SDK.",
            "QA was the hardest part. We invested in automated capture rigs that sweep every combination of preset, renderer, and upscaler. The rigs compare frame pacing metrics and highlight anomalies before builds reach players.",
            "If you're a mid-sized studio, abstract vendor-specific hooks early. Waiting until late beta will derail your stabilization schedule."
        ],
        "status": "published",
    },
    {
        "category": "Game Development",
        "title": "Unreal Engine 5 Streaming World Partition at MMO Scale",
        "summary": "Our experience adapting UE5 World Partition for a 2000-concurrent-player shared world.",
        "body": [
            "World Partition unlocks seamless worlds, but MMO requirements expose scaling issues. We introduced a dynamic cell prioritization algorithm that factors in player velocity, event density, and quest importance. The result: 84% reduction in hitches when 300 players converge on a single zone.",
            "We also decoupled replication. NPC AI now runs server-side microservices, pushing state changes to clients through a custom replication layer. This kept server tick rates stable even during raid encounters.",
            "For studios exploring UE5, prototype World Partition with your heaviest multiplayer scenarios early. Tuning cell sizes and streaming budgets sooner will save months later."
        ],
        "status": "published",
    },
    {
        "category": "Game Development",
        "title": "Building Ethical Monetization Systems Players Actually Trust",
        "summary": "How our live-ops team redesigned monetization around transparency and reduced churn by 12%.",
        "body": [
            "Loot boxes are losing favor, so we pivoted to a transparent mastery track. Players see every reward upfront, and bundles include gameplay value rather than cosmetic fluff. Churn dropped 12% within two months.",
            "We analyze spending telemetry weekly, watching for patterns that hint at buyer's remorse. When metrics spike, we adjust pricing or introduce make-good events. Community trust skyrocketed because transparency is part of our marketing, not an afterthought.",
            "If you're building a live service in 2025, assume your audience has zero tolerance for opaque monetization. Design systems that respect time and wallets, and retention numbers will follow."
        ],
        "status": "published",
    },
]


AUTHOR_SPECS = [
    {"username": "alex.kim", "first_name": "Alex", "last_name": "Kim", "email": "alex.kim@cetix.demo"},
    {"username": "priya.nair", "first_name": "Priya", "last_name": "Nair", "email": "priya.nair@cetix.demo"},
    {"username": "mateo.ferrara", "first_name": "Mateo", "last_name": "Ferrara", "email": "mateo.ferrara@cetix.demo"},
    {"username": "sara.chen", "first_name": "Sara", "last_name": "Chen", "email": "sara.chen@cetix.demo"},
    {"username": "dmitry.ivanov", "first_name": "Dmitry", "last_name": "Ivanov", "email": "dmitry.ivanov@cetix.demo"},
    {"username": "lena.rojas", "first_name": "Lena", "last_name": "Rojas", "email": "lena.rojas@cetix.demo"},
]


READER_SPECS = [
    {"username": "noah.reader", "first_name": "Noah", "last_name": "Reid", "email": "noah.reid@cetix.demo"},
    {"username": "amira.reader", "first_name": "Amira", "last_name": "Saleh", "email": "amira.saleh@cetix.demo"},
    {"username": "olivia.reader", "first_name": "Olivia", "last_name": "Martens", "email": "olivia.martens@cetix.demo"},
]


class Command(BaseCommand):
    help = "Seed the database with demo users, articles, and engagement metrics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush-existing",
            action="store_true",
            help="Delete previously seeded demo articles before creating new ones.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            categories = self._ensure_categories()
            authors = self._ensure_users(AUTHOR_SPECS, role=User.ROLE_ADMIN)
            readers = self._ensure_users(READER_SPECS, role=User.ROLE_USER)
            all_users = authors + readers

            if options["flush_existing"]:
                Article.objects.filter(title__in=[item["title"] for item in ARTICLE_DATA]).delete()

            created_articles = []

            for article_spec in ARTICLE_DATA:
                article = self._create_article(article_spec, categories, authors)
                if article:
                    created_articles.append(article)

            self.stdout.write(self.style.SUCCESS(f"Created {len(created_articles)} articles."))

            for article in created_articles:
                self._seed_interactions(article, all_users)

            self.stdout.write(self.style.SUCCESS("Engagement metrics applied. Seeding complete."))

    def _ensure_categories(self):
        categories = {}
        for name in ["Backend", "Frontend", "AI", "Cyber Security", "Cyber Sport", "Game Development"]:
            category, _ = Category.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" ", "-")})
            categories[name] = category
        return categories

    def _ensure_users(self, specs, role):
        users = []
        for spec in specs:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "role": role,
                },
            )
            if created:
                user.set_password("cetix123")
                user.role = role
                user.is_active = True
                if role == User.ROLE_ADMIN:
                    user.is_staff = True
                user.save()
            else:
                if user.role != role:
                    user.role = role
                    if role == User.ROLE_ADMIN:
                        user.is_staff = True
                    user.save(update_fields=["role", "is_staff"])
            users.append(user)
        return users

    def _create_article(self, spec, categories, authors):
        existing = Article.objects.filter(title=spec["title"]).first()
        if existing:
            if self._ensure_article_cover(existing, spec["category"]):
                self.stdout.write(f"Attached cover image to existing article: {spec['title']}")
            else:
                self.stdout.write(f"Skipping existing article: {spec['title']}")
            return None

        category = categories[spec["category"]]
        author = random.choice(authors)
        created_at = timezone.now() - timedelta(days=random.randint(5, 90))

        article = Article(
            title=spec["title"],
            author=author,
            category=category,
            content="\n\n".join(textwrap.fill(par, width=110) for par in spec["body"]),
            status=spec.get("status", Article.STATUS_PUBLISHED),
        )
        article.save()

        image_content, filename = self._fetch_image(category.name, spec["title"])
        article.cover_image.save(filename, image_content)

        if article.status == Article.STATUS_PUBLISHED:
            article.published_at = created_at + timedelta(hours=random.randint(6, 48))
        else:
            article.published_at = None

        Article.objects.filter(pk=article.pk).update(
            created_at=created_at,
            updated_at=created_at,
            published_at=article.published_at,
            status=article.status,
        )
        article.refresh_from_db()
        return article

    def _ensure_article_cover(self, article, category_name):
        if article.cover_image or article.external_cover_url:
            return False
        fallback_urls = CATEGORY_IMAGE_SOURCES.get(category_name, [])
        if not fallback_urls:
            return False
        article.external_cover_url = f"{fallback_urls[0]}?auto=format&fit=crop&w=1400&q=80"
        article.save(update_fields=["external_cover_url"])
        return True

    def _fetch_image(self, category_name, title):
        urls = CATEGORY_IMAGE_SOURCES.get(category_name, [])[:]
        random.shuffle(urls)
        for url in urls:
            try:
                response = requests.get(f"{url}?auto=format&fit=crop&w=1400&q=80", timeout=10)
                response.raise_for_status()
                filename = f"{title.lower().replace(' ', '-')}.jpg"
                return ContentFile(response.content), filename
            except requests.RequestException:
                continue
        return self._generate_placeholder(category_name, title)

    def _generate_placeholder(self, category_name, title):
        width, height = 1400, 900
        background_color = (18, 28, 45)
        accent_color = (59, 130, 246)
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0, height - 260), (width, height)], fill=(10, 17, 30))

        font = ImageFont.load_default()
        draw.text((60, height - 200), category_name.upper(), fill=accent_color, font=font)
        draw.text((60, height - 150), textwrap.shorten(title, width=60, placeholder="..."), fill=(226, 232, 240), font=font)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        filename = f"{category_name.lower().replace(' ', '-')}-{random.randint(1000,9999)}.jpg"
        return ContentFile(buffer.getvalue()), filename

    def _seed_interactions(self, article, users):
        potential_users = [u for u in users if u != article.author]
        if not potential_users:
            return

        like_pool = random.sample(potential_users, k=random.randint(3, min(6, len(potential_users))))
        for user in like_pool:
            value = ArticleReaction.VALUE_LIKE if random.random() > 0.2 else ArticleReaction.VALUE_DISLIKE
            ArticleReaction.objects.update_or_create(
                article=article,
                user=user,
                defaults={"value": value},
            )

        bookmark_users = random.sample(potential_users, k=random.randint(1, min(3, len(potential_users))))
        for user in bookmark_users:
            Bookmark.objects.get_or_create(article=article, user=user)

        comment_users = random.sample(potential_users, k=random.randint(1, min(4, len(potential_users))))
        parents = []
        for user in comment_users:
            body = random.choice(COMMENT_SNIPPETS).format(topic=article.category.name.lower())
            comment = ArticleComment.objects.create(
                article=article,
                user=user,
                body=body,
            )
            parents.append(comment)

        if parents and random.random() > 0.5:
            reply_user = random.choice(potential_users)
            parent = random.choice(parents)
            ArticleComment.objects.create(
                article=article,
                user=reply_user,
                parent=parent,
                body=random.choice(COMMENT_SNIPPETS).format(topic=article.category.name.lower()),
            )


