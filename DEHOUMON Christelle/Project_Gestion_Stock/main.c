#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define MAX_PRODUCTS 500
#define MAX_NAME_LENGTH 100

// la structure d'un produit que je represente ainsi
typedef struct
{
	int id ;
	char name [MAX_NAME_LENGTH];
	int quantity;
	float price;
}Product;

Product products [MAX_PRODUCTS]; 	// tableau de stockage du produit
int product_count = 0;				// le compteur des produits en stock initialiser à 0

void clear()
{
	int c;
	while((c = getchar()) != '\n' && c != EOF);		// lit tous les caractères jusqu'au retour à la ligne

}

int gen_newID()		// cette fonction permet la generation de l'ID automatiquement
{
	if (product_count == 0) return 1;
    int max_id = 0;
	for (int i = 0; i < product_count; i++) 
	{
        if (products[i].id > max_id) 
		{
            max_id = products[i].id;
        }
    }
    return max_id + 1;
}

void add_Product();
void edit_Product();
void delete_Product();
void display_Product();
void search_Product();
void saveTo_CSV();
void loadFrom_CSV();

// la fonction principal 
int main()
{
	loadFrom_CSV();		// Charge les produits au demarrage
	
	int choice;

	do{
	printf("*******************************************************************************************\n");
	printf("                               INVENTORY MANAGEMENT SYSTEM\n");
	printf("*******************************************************************************************\n");
		
		
		puts("");
		// affichage du menu

	printf("1. Register a new product\n");
	printf("2. Update  existing product(s))\n");
	printf("3. Remove a product\n");
	printf("4. View all products in your stock\n");
	printf("5. Search for a product\n");
	printf("6. Save changes and exit\n");
	printf("\n");
	printf("Please select an option(1-6): ");
	scanf("%d", &choice);
		
		// execution de l'action choisie se fait par cette structure
		switch (choice)
		{
		case 1:
			add_Product();
			break;
		case 2:
			edit_Product();
			break;

		case 3:
			delete_Product();
			break;

		case 4:
			display_Product();
			break;

		case 5:
			search_Product();
			break;

		case 6:
			saveTo_CSV();
		
			break;

		default:
			printf("Invalid Option! Please review our instructions.\n");
		}
	} while (choice != 6); 		// repete jusqu'à ce que tu choisisse de quitter

	return 0;

}
// cette structure est pour la fonction d'ajout des produits
void add_Product()
{
	if (product_count >= MAX_PRODUCTS)
	{
		printf("Sorry but the stock is full, impossible to add more products.\n");

		return;
	}
	
	// Creation d'un nouveau produit
	Product newProduct;
	newProduct.id = gen_newID();

	printf("Please enter the product's name : ");
	puts("");
	clear();
	fgets(newProduct.name, MAX_NAME_LENGTH, stdin); 	// lecture de toute la ligne même les espaces 
	newProduct.name[strcspn(newProduct.name, "\n")] = '\0';  // cette fonction enève le retour à la ligne

	printf("Enter the quantity of your product : ");
	scanf("%d", &newProduct.quantity);
	clear();
	
	printf("Please enter the price : ");
	scanf("%f", &newProduct.price);
	clear();

	products[product_count++] = newProduct;
	printf("\n");
	printf("Product added sucessfully ; Your product's(ID: %d)\n", newProduct.id);
	printf("\n");
	puts("");
}

// fonction de la modfication du produit 
void edit_Product()
{
	int id;

	printf("Enter the ID of the product to be modified: ");
	scanf("%d", &id);
	clear();
	

	for (int i = 0; i < product_count; i++) 	//Cherche le produit
	{
		if (products[i].id == id)
		{
			printf("Enter the new name of the product : ");
			fgets(products[i].name, MAX_NAME_LENGTH, stdin);
			products[i].name[strcspn(products[i].name, "\n")] = '\0';

			printf("Enter the new quantity: ");
			scanf("%d", &products[i].quantity);
			clear();
			
			printf("Enter the new price: ");
			scanf("%f", &products[i].price);
			clear();

	printf("............................................................................................\n");
	printf("Your product has been updated successfully\n");
	printf("............................................................................................\n");
			printf("\n");	
			return;
		}

	}
	printf("............................................................................................\n");
	printf("We are sorry but there is No products found with this ID.\n");
	printf("............................................................................................\n");
	printf("\n");
}

//structure de suppression du produit 
void delete_Product()
{
	int id;

	printf("Enter the ID of product to be deleted: ");
	scanf("%d", &id);
	clear();

	for (int i = 0; i < product_count; i++)
	{
		if (products[i].id == id)
		{
			for (int j = i; j < product_count - 1; j++)
			{
				products[j] = products[j + 1];
			}
			product_count--;
	printf("............................................................................................\n");
	printf("The old product has been deleted successfully\n");
	printf("............................................................................................\n");
	printf("\n");
			return;
		}

	}
	printf("There is No products found with this ID.\n");
}


// structure de l'affichage des produits qui sont dans le stock
void display_Product()
{
	if (product_count == 0)
	{
		printf("No products available.\n");
		return;
	}
	printf("\nProducts List:\n");
	printf("\n%-8s %-30s %-10s %-10s\n", "ID", "Name", "Quantity", "Price");
	
	printf("\n");

	for (int i = 0; i < product_count; i++)
	{
		printf("%-8d %-30s %-10d %-9.2f FCFA\n", products[i].id, products[i].name, products[i].quantity, products[i].price);
	}

}


// stucture de la recherche des produits voulu par ID ou Nom
void search_Product()
{
	int choice;
	printf("Research by:\n1.Name\n2.ID\n3.Your Choice: ");
	scanf("%d", &choice);
	clear();

	if (choice == 1)
	{	char name[100];
		printf("Enter the name of product: ");
		fgets(name, sizeof(name), stdin);
		name[strcspn(name, "\n")] = '\0';
		
		printf("\n Found products:\n");
		printf("\n%-8s %-30s %-10s %-10s\n", "ID", "Name", "Quantity", "Price");
		
	printf("\n");
		
		int found = 0;
		for (int i = 0; i < product_count; i++)
		{
			if (strstr(products[i].name, name) != NULL)
			{
				printf("%-8d %-30s %-10d %-9.2f FCFA\n", products[i].id, products[i].name, products[i].quantity, products[i].price); 
				
				found = 1;
			}

		}
		if(!found)printf("Product not found.\n");
	}
	else if (choice == 2)
	{
		int id;
		printf("Enter the ID of product: ");
		scanf("%d", &id);
		
		printf("\n Found products:\n");
		printf("\n%-8s %-30s %-10s %-10s\n", "ID", "Name", "Quantity", "Price");
		
		printf("\n");
		
		int found = 0;
		for (int i = 0; i < product_count; i++)
		{
			if (products[i].id == id)
			{
				printf("%-8d %-30s %-10d %-9.2f FCFA \n", products[i].id, products[i].name, products[i].quantity, products[i].price);

				found = 1;
				break;
			}

		}
		if(!found)printf("Product not found.\n");
	}
	else
	{
		printf("Invalid Choice.\n");
		
	}

}

// structure pour la sauvegarde dans le fichier CSV
void saveTo_CSV()
{
	FILE*file = fopen("stock.csv", "w");	// ouverture du fichier

	if (!file)
	{
		printf("Unable to open file for writing.\n");
		return;
	}
	fprintf(file,  "ID, Name, Quantity, Price\n");
	for (int i = 0; i < product_count; i++)
	{
		fprintf(file, "%d,%s,%d,%.2f\n", products[i].id, products[i].name, products[i].quantity,  products[i].price);
	}

	fclose(file);	// fermeture du fichier
//	printf("          ================================================================================          \n");
	printf("\nThank you for using the inventory management system! Your products have been successfully saved in the 'stock.csv'.\n");
	printf("                 *--------------------------------------------------------------*          \n");
	printf("\n");
}


//structure de chargement du fichier
void loadFrom_CSV()
{
	FILE*file = fopen("stock.csv", "r");
	if (!file)
	{
		printf("File 'stock.csv' not be found.\n New empty stock.\n");
		return;
	}

	char line[256];
	fgets(line, sizeof(line), file);
	
	product_count = 0;
	
	//lit chaque ligne du fichier
	while (fgets(line, sizeof(line), file) && product_count < MAX_PRODUCTS)
	{
		Product p;
		
		// extrait chaque valeurs separées par des virgules si tu regarde bien dans le fichier csv l'ID, le nom... sont separées par des virgules
		if(sscanf(line, "%d, %99[^,], %d, %f", &p.id, p.name, &p.quantity, &p.price) == 4)
		{
			products[product_count++]=p;	// ajout du produit dans le stock
		}
	
	}

	fclose(file);
	printf("Loading complete. %d products loaded.\n", product_count);	//le nombres de produits stockés
	puts("");

}
