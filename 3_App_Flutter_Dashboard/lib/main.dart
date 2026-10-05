import 'package:flutter/material.dart';

void main() {
  runApp(const DashboardApp());
}

class DashboardApp extends StatelessWidget {
  const DashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Dashboard de Ventas',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final metrics = [
      Metric('Ingresos', '\$12.4M', '+8.2%', Icons.attach_money, Colors.green),
      Metric('Clientes', '1,248', '+12%', Icons.people, Colors.blue),
      Metric('Pedidos', '356', '-3%', Icons.shopping_bag, Colors.orange),
      Metric('Tasa conversión', '4.6%', '+1.1%', Icons.trending_up, Colors.purple),
    ];

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: 0,
            onDestinationSelected: (_) {},
            labelType: NavigationRailLabelType.selected,
            destinations: const [
              NavigationRailDestination(icon: Icon(Icons.dashboard), label: Text('Inicio')),
              NavigationRailDestination(icon: Icon(Icons.analytics), label: Text('Análisis')),
              NavigationRailDestination(icon: Icon(Icons.people), label: Text('Clientes')),
              NavigationRailDestination(icon: Icon(Icons.settings), label: Text('Ajustes')),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Panel de control', style: Theme.of(context).textTheme.headlineSmall),
                  const SizedBox(height: 8),
                  Text('Resumen de ventas · Octubre 2026', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey)),
                  const SizedBox(height: 24),
                  Expanded(
                    child: GridView.count(
                      crossAxisCount: 4,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      childAspectRatio: 1.4,
                      children: metrics.map((m) => MetricCard(metric: m)).toList(),
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Row(
                      children: [
                        Expanded(
                          child: Card(
                            child: Padding(
                              padding: const EdgeInsets.all(20.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Ventas semanales', style: Theme.of(context).textTheme.titleMedium),
                                  const SizedBox(height: 16),
                                  Expanded(child: BarChart()),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        const Expanded(child: RecentActivity()),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class Metric {
  final String title;
  final String value;
  final String change;
  final IconData icon;
  final Color color;

  Metric(this.title, this.value, this.change, this.icon, this.color);
}

class MetricCard extends StatelessWidget {
  final Metric metric;
  const MetricCard({super.key, required this.metric});

  @override
  Widget build(BuildContext context) {
    final isPositive = metric.change.startsWith('+');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                CircleAvatar(backgroundColor: metric.color.withOpacity(0.15), child: Icon(metric.icon, color: metric.color, size: 20)),
                Chip(
                  label: Text(metric.change, style: const TextStyle(fontSize: 12)),
                  backgroundColor: isPositive ? Colors.green.shade50 : Colors.red.shade50,
                  side: BorderSide.none,
                  labelStyle: TextStyle(color: isPositive ? Colors.green.shade700 : Colors.red.shade700),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(metric.value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                Text(metric.title, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class BarChart extends StatelessWidget {
  final List<double> values = const [40, 70, 55, 90, 65, 85, 75];

  const BarChart({super.key});

  @override
  Widget build(BuildContext context) {
    final max = values.reduce((a, b) => a > b ? a : b);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: values.asMap().entries.map((entry) {
        final day = ['L', 'M', 'X', 'J', 'V', 'S', 'D'][entry.key];
        return Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Container(
              width: 28,
              height: 120 * (entry.value / max),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
                borderRadius: BorderRadius.circular(6),
              ),
            ),
            const SizedBox(height: 8),
            Text(day, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        );
      }).toList(),
    );
  }
}

class RecentActivity extends StatelessWidget {
  const RecentActivity({super.key});

  @override
  Widget build(BuildContext context) {
    final items = [
      ('Nueva venta', 'Hace 5 min', '+\$450.000'),
      ('Cliente registrado', 'Hace 12 min', 'Andrea López'),
      ('Pedido enviado', 'Hace 30 min', '#10234'),
      ('Pago recibido', 'Hace 1 h', '+\$1.200.000'),
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Actividad reciente', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.separated(
                itemCount: items.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (context, index) {
                  final (title, time, detail) = items[index];
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const CircleAvatar(child: Icon(Icons.notifications_none, size: 18)),
                    title: Text(title),
                    subtitle: Text(time, style: const TextStyle(color: Colors.grey)),
                    trailing: Text(detail, style: const TextStyle(fontWeight: FontWeight.bold)),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
