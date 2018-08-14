from jet.dashboard.modules import DashboardModule


class SiteMap(DashboardModule):
    title = 'Sitemap'
    template = 'admin/dashboard_modules/sitemap.html'
    draggable = False
    deletable = False
    collapsible = False
