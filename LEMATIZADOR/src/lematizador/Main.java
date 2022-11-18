package lematizador;

import java.util.*;
import java.io.*;
import br.usp.nilc.unitex.Lexicon;
import java.util.regex.Pattern;
/**
 *
 * @author Erick
 */
public class Main {
    public static void main(String[] args) {
        PrintStream saidapadrao = new PrintStream(System.out);
        ArrayList tokens = new ArrayList();
        toker t = new toker();
        String arquivo = args[0];
        saidapadrao.println("Wait...");
        
        //arquivo de saida
        try
        {
            PrintStream saida = new PrintStream(new File(arquivo+".out"));
            //se desejar exibir apenas o lema das palavras do texto de entrada, 
            //adicionar o argument "nf" apos o nome do arquivo de entrada
            String exibe_flexionada = "f";
            if ((args.length > 1))
            {
                exibe_flexionada = args[1];
            }

            try
            {
                tokens = t.tokenizaArquivo(arquivo); // faz a tokenizacao do arquivo de entrada
            }
            catch(Exception e)
            {
                saidapadrao.println("Erro "+e);
            }

            lemmar l = new lemmar();

            //cria arquivo temporario para MXPOST e grava os tokens nesse arquivo
            try
            {
                File arquivoMXPOST = new File(arquivo+".mxp");
                PrintWriter saidaMXP = new PrintWriter(new FileWriter(arquivoMXPOST));
                //para cada token do arquivo de entrada
                for (int k=0; k<tokens.size(); k++)
                {
                    saidaMXP.print(tokens.get(k).toString()+" ");
                }
                saidaMXP.close();
            }
            catch(Exception e)
            {
                saidapadrao.println("Erro mxp:"+e); 
            }

            //chama o MXPOST e faz a etiquetacao do arquivo de entrada
            tagger etiquetador = new tagger(arquivo+".mxp",arquivo+".tagged");

            //Abre arquivo temporario gerado pelo MXPOST
            File arquivoMXPOST = new File(arquivo+".tagged");
            FileReader reader = new FileReader(arquivoMXPOST);
            BufferedReader leitor = new BufferedReader(reader);
            String linha;
            //para cada token do arquivo de entrada
            while ((linha = leitor.readLine()) != null)
            {
                String[] palavras_aux = linha.split(" ");
                ArrayList palavras = new ArrayList();
                
                //pre-processamento para separar verbos hifenizados
                for (int p=0; p<palavras_aux.length; p++)
                {
                  String[] partes = palavras_aux[p].split("_");
                  if ((partes[1].startsWith("VERB")) && (!(partes[0].startsWith("new-paragraph"))))     
                  {
                      int counter = 0;
                      for(int s=1; s<(partes[0].length()-2);s++)
                      {
                          if (partes[0].charAt(s) == '-')
                          {
                              counter++;
                          }
                      }
                      if (counter == 1)
                      {
                          String[] aux = partes[0].split("-");
                          palavras.add(aux[0]+"_VERB");
                          palavras.add("(-"+aux[1]+"[enc])_PRON");
                      }
                      else if (counter == 2)
                      {
                          String[] aux = partes[0].split("-");
                          palavras.add(aux[0]+aux[2]+"_VERB");
                          palavras.add("(-"+aux[1]+"[mes])_PRON");
                      }
                      else
                      {
                          palavras.add(partes[0]+"_VERB");
                      }
                  }
                  else
                  {
                      palavras.add(palavras_aux[p]);
                  }
                }

                //para cada token do texto de entrada
                for (int p=0; p<palavras.size(); p++)
                {
                    saidapadrao.println((p*100)/palavras.size()+"% completed...");
                    //para cada palavra
                    
                    String[] partes = palavras.get(p).toString().split("_");
                    String flexionada = partes[0];
                    String tag = partes[1];
                    int imprimiu = 0;

                    if (partes[0].trim().equals("new-paragraph"))
                    {
                        saidapadrao.println("paragraph...");
                        saida.println();
                        continue;
                    }
                    
                    
                    //se a palavra for nome proprio ou preposicao (apenas),
                    //retorna a propria palavra flexionada
                    if ((tag.equals("NP")) || (tag.equals("PREP")))
                    {
                        if (exibe_flexionada.equals("nf"))
                        {
                            saida.print(flexionada);
                        }
                        else
                        {
                            saida.print(flexionada+"/"+flexionada);
                        }
                        imprimiu = 1;
                    }
                    else
                    {
                        //usa o UNITEX para obter os possiveis lemas
                        ArrayList<String> r = new ArrayList<String>();
                        r = l.lemma(flexionada.toLowerCase(), "unitex-pb.inf", "Alphabet.txt");
                        
                        //se retornado algum lema, mapeia na classe retornada do MXPOST
                        String todos_lemmas = "";
                        for(int i=0; i<r.size(); i++)
                        {
                            //saida.println("\n"+flexionada+"->"+r.get(i).toString());
                            partes = r.get(i).toString().split(",");
                            String[] partes2 = partes[1].split("\\.");
                            String lemma = partes2[0];
                            partes = partes2[1].split(":");
                            String tag_lemma = partes[0];
                                
                            //mapeamento entre as tags do MXPOST e do UNITEX
                            map m = new map();
                            String lemma_retorno = m.mapeia(flexionada, tag, lemma, tag_lemma);
                            if (!(lemma_retorno.equals("not_found")))
                            {
                                if (!(todos_lemmas.contains(lemma_retorno)))
                                {
                                    todos_lemmas += "/"+lemma_retorno;
                                }
                            }
                        }
                        if (todos_lemmas.equals(""))
                        {
                            todos_lemmas="/"+flexionada;
                        }
                        if (exibe_flexionada.equals("nf"))
                        {
                            saida.print(todos_lemmas.substring(1));
                            imprimiu = 1;
                        }else
                        {
                            saida.print(flexionada+todos_lemmas);
                            imprimiu = 1;
                        }
                    }
                    if (imprimiu == 0)
                    {
                        if (exibe_flexionada.equals("nf"))
                        {
                            saida.print(flexionada);
                        }
                        else
                        {
                            saida.print(flexionada+"/"+flexionada);
                        }
                    }
                    saida.print(" ");
                }   
                saida.println();
            }
            leitor.close();
        }
        catch(Exception e)
        {
            saidapadrao.println("Erro2: "+e); 
        }
        saidapadrao.println("Finished!");
    }
}