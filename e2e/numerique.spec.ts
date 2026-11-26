import { expect } from "@playwright/test"
import { test } from "./fixtures"

// These scenarios rely on the content created by
// `python manage.py create_e2e_pages` (numerique_gouv app).

test.describe("News", () => {
  test(
    "the news index renders",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/actualites/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.getByRole("heading", { level: 1 })).toContainText("Actualités")
      await expect(main.getByRole("link", { name: "Lancement de l’offre d’accompagnement IA" })).toBeVisible()
      await expect(main.getByRole("link", { name: "Nouvelle stratégie cloud de l’État" })).toBeVisible()
    },
  )

  test("filtering by tag narrows the list", async ({ page }) => {
    await page.goto("/actualites/")
    const main = page.locator("main")
    await main.locator("a.fr-tag", { hasText: "Intelligence artificielle" }).click()

    await expect(page).toHaveURL(/page_tag=ia/)
    await expect(main.locator("a.fr-tag", { hasText: "Intelligence artificielle" })).toHaveAttribute(
      "aria-pressed",
      "true",
    )
    await expect(main.getByRole("link", { name: "Lancement de l’offre d’accompagnement IA" })).toBeVisible()
    await expect(main.getByRole("link", { name: "L’IA au service des agents publics" })).toBeVisible()
    await expect(main.getByRole("link", { name: "Ouverture des données publiques" })).toHaveCount(0)
  })

  test("a news post renders", async ({ page }) => {
    const response = await page.goto("/actualites/nouvelle-strategie-cloud/")
    expect(response?.status()).toBe(200)
    await expect(page.locator("main h1")).toContainText("Nouvelle stratégie cloud de l’État")
  })

  test("the date of a news post links to the posts of the same year", async ({ page }) => {
    await page.goto("/actualites/nouvelle-strategie-cloud/")
    await page.locator("main").getByRole("link", { name: /2025/ }).click()

    await expect(page).toHaveURL(/\/actualites\/\?year=2025$/)
    const main = page.locator("main")
    await expect(main.getByRole("link", { name: "Nouvelle stratégie cloud de l’État" })).toBeVisible()
    await expect(main.getByRole("link", { name: "Ouverture des données publiques" })).toBeVisible()
    await expect(main.getByRole("link", { name: "L’IA au service des agents publics" })).toHaveCount(0)
  })

  test("an unknown filter returns a 404", async ({ page }) => {
    const response = await page.goto("/actualites/?page_tag=inconnu")
    expect(response?.status()).toBe(404)
  })
})

test.describe("Offers", () => {
  test(
    "the offers index renders",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/offre-accompagnement/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.getByText("Albert, l’IA des agents publics").first()).toBeVisible()
      await expect(main.getByText("Fonds pour la transformation de l’action publique").first()).toBeVisible()
    },
  )

  test("filtering by tag narrows the offers", async ({ page }) => {
    await page.goto("/offre-accompagnement/")
    const main = page.locator("main")
    await main.locator("a.fr-tag", { hasText: "Intelligence artificielle" }).click()

    await expect(page).toHaveURL(/page_tag=ia/)
    await expect(main.getByText("Albert, l’IA des agents publics").first()).toBeVisible()
    await expect(main.getByText("France transfert")).toHaveCount(0)
  })

  test("the “See more” button reveals the hidden expertises", async ({ page }) => {
    await page.goto("/offre-accompagnement/")
    const expertises = page.locator(".expertise-subpage")
    const button = page.locator("#voir-plus-expertises")

    await expect(expertises).toHaveCount(8)
    await expect(expertises.locator("visible=true")).toHaveCount(6)
    await expect(button).toHaveAttribute("aria-expanded", "false")

    await button.click()

    await expect(expertises.locator("visible=true")).toHaveCount(8)
    await expect(button).toBeHidden()
    await expect(button).toHaveAttribute("aria-expanded", "true")
  })
})

test.describe("Digital services", () => {
  test(
    "the services index renders",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/services-numeriques/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.getByText("ProConnect").first()).toBeVisible()
      await expect(main.getByText("FranceConnect").first()).toBeVisible()
      await expect(main.getByText("API Entreprise").first()).toBeVisible()
    },
  )

  test("a service page redirects to the services index", async ({ page }) => {
    await page.goto("/services-numeriques/proconnect/")
    await expect(page).toHaveURL(/\/services-numeriques\/$/)
  })
})

test.describe("Hub page", () => {
  test(
    "the hub page gathers the content linked to its tag",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/hub-intelligence-artificielle/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.getByRole("link", { name: "Lancement de l’offre d’accompagnement IA" })).toBeVisible()
      await expect(main.getByRole("link", { name: "Conseil en intelligence artificielle" })).toBeVisible()
      await expect(main.getByText("ProConnect").first()).toBeVisible()
      await expect(main.getByText("Ouverture des données publiques")).toHaveCount(0)
    },
  )
})

test.describe("Sitemap", () => {
  test(
    "the sitemap lists the published pages",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/a-propos-numerique/carte-du-site/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.locator(`a[href="/actualites/"]`)).toHaveText("Actualités")
      await expect(main.getByRole("link", { name: "Services numériques", exact: true })).toBeVisible()
    },
  )
})

test.describe("Search", () => {
  test("the header search bar finds a published page", async ({ page }) => {
    await page.goto("/")
    const input = page.locator("header #search-bar-input")
    await input.fill("France transfert")
    await input.press("Enter")

    await expect(page).toHaveURL(/q=France\+transfert/)
    const main = page.locator("main")
    await expect(main.getByRole("heading", { level: 1 })).toContainText("France transfert")
    await expect(main.getByRole("link", { name: "France transfert" })).toBeVisible()
  })
})

test.describe("Slider", () => {
  test(
    "the slider renders its controls",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/rejoignez-nous/")
      expect(response?.status()).toBe(200)
      const slider = page.locator("[data-ng-slider]")
      await expect(slider.getByRole("heading", { name: "Ils et elles témoignent" })).toBeVisible()
      await expect(slider.locator(".ng-slider__controls")).toBeVisible()
      await expect(slider.locator(".ng-slider__marker")).toHaveCount(3)
    },
  )

  test("the buttons move between slides and wrap around", async ({ page }) => {
    await page.goto("/rejoignez-nous/")
    const slider = page.locator("[data-ng-slider]")
    const markers = slider.locator(".ng-slider__marker")
    const previous = slider.getByRole("button", { name: "Diapositive précédente" })
    const next = slider.getByRole("button", { name: "Diapositive suivante" })

    await expect(markers.nth(0)).toHaveAttribute("aria-current", "true")

    await next.click()
    await expect(markers.nth(1)).toHaveAttribute("aria-current", "true")
    await expect(markers.nth(0)).not.toHaveAttribute("aria-current")

    await previous.click()
    await expect(markers.nth(0)).toHaveAttribute("aria-current", "true")

    // "Previous" on the first slide goes to the last one
    await previous.click()
    await expect(markers.nth(2)).toHaveAttribute("aria-current", "true")
    await expect(slider.getByText("Trouver des solutions est un défi passionnant")).toBeInViewport()

    // "Next" on the last slide goes back to the first one
    await next.click()
    await expect(markers.nth(0)).toHaveAttribute("aria-current", "true")

    await markers.nth(1).click()
    await expect(markers.nth(1)).toHaveAttribute("aria-current", "true")
  })
})

test.describe("Item grid", () => {
  test(
    "the grid shows the first items and a “See more” button",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/numerique-etat/")
      expect(response?.status()).toBe(200)
      const items = page.locator(".item-grid-element")
      await expect(items).toHaveCount(10)
      await expect(items.locator("visible=true")).toHaveCount(4)
      await expect(page.getByRole("button", { name: "Voir plus" })).toBeVisible()
    },
  )

  test("the “See more” button reveals the hidden items", async ({ page }) => {
    await page.goto("/numerique-etat/")
    const items = page.locator(".item-grid-element")
    const button = page.getByRole("button", { name: "Voir plus" })

    await button.click()

    await expect(items.locator("visible=true")).toHaveCount(10)
    await expect(page.getByText("Direction du numérique n° 10")).toBeVisible()
    await expect(button).toBeHidden()
  })
})

// The contact form is created by `create_starter_pages`, like the one used on numerique.gouv.fr
test.describe("Contact form", () => {
  test(
    "the contact form renders",
    { tag: "@regression" },
    async ({ page }) => {
      const response = await page.goto("/contact/")
      expect(response?.status()).toBe(200)
      const main = page.locator("main")
      await expect(main.getByRole("heading", { level: 1 })).toContainText("Contact")
      await expect(main.getByRole("textbox", { name: /^Votre nom complet/ })).toBeVisible()
      await expect(main.getByRole("textbox", { name: /^Votre adresse électronique/ })).toBeVisible()
      await expect(main.getByRole("textbox", { name: /^Votre message/ })).toBeVisible()
    },
  )

  test("submitting the form shows the thank you text", async ({ page }) => {
    await page.goto("/contact/")
    const main = page.locator("main")
    await main.getByRole("textbox", { name: /^Votre nom complet/ }).fill("Camille Dupont")
    await main.getByRole("textbox", { name: /^Votre adresse électronique/ }).fill("camille.dupont@example.com")
    await main.getByRole("textbox", { name: /^Titre de votre message/ }).fill("Message de test")
    await main.getByRole("textbox", { name: /^Votre message/ }).fill("Bonjour, ceci est un message de test.")

    // The honeypot rejects the submissions sent less than 3 seconds after the page load
    await page.waitForTimeout(3500)
    await main.getByRole("button", { name: "Envoyer le formulaire" }).click()

    await expect(main.getByText("Merci pour votre message !")).toBeVisible()
  })
})
